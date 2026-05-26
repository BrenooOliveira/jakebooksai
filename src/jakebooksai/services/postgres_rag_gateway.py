"""Postgres-backed retrieval gateway for catalog, stock, and recommendation queries."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
import re
import unicodedata
from typing import Any

import psycopg
from psycopg.rows import dict_row

from .contracts import RagGateway
from .rag_stub import InMemoryRagGateway


@dataclass(frozen=True, slots=True)
class _BookCandidate:
    """Book row enriched with catalog metadata, stock, and order history."""

    titulo: str
    sinopse: str
    valor_venda: float | None
    estoque_quantidade: int | None
    autores: tuple[str, ...]
    categorias: tuple[str, ...]
    total_vendido: int
    total_pedidos: int
    ultimo_pedido: date | None


class PostgresRagGateway(RagGateway):
    """Retrieve book, stock, and purchase-history snippets from a local Postgres database."""

    def __init__(
        self,
        host: str,
        port: int,
        dbname: str,
        user: str,
        password: str,
        *,
        limit: int = 5,
        fallback_gateway: RagGateway | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._dbname = dbname
        self._user = user
        self._password = password
        self._limit = limit
        self._fallback_gateway = fallback_gateway or InMemoryRagGateway()

    def retrieve(self, query: str) -> list[str]:
        """Return ranked snippets for availability, purchase history, or recommendations."""
        clean_query = query.strip()
        intent = self._detect_intent(clean_query)

        try:
            candidates = self._load_candidates()
        except psycopg.Error:
            return self._fallback_gateway.retrieve(query)

        if not candidates:
            return self._fallback_gateway.retrieve(query)

        author_popularity, category_popularity = self._build_affinity_maps(candidates)
        matched_candidates = self._filter_candidates(candidates, clean_query)
        ranked_candidates = sorted(
            matched_candidates,
            key=lambda candidate: self._score_candidate(
                candidate,
                clean_query,
                intent,
                author_popularity,
                category_popularity,
            ),
            reverse=True,
        )

        snippets = [
            self._format_snippet(candidate, intent=intent)
            for candidate in ranked_candidates[: self._limit]
        ]
        return snippets or self._fallback_gateway.retrieve(query)

    def _load_candidates(self) -> list[_BookCandidate]:
        """Load active books and their aggregated sales history from Postgres."""
        query = """
            WITH sales AS (
                SELECT
                    l.id AS livro_id,
                    COALESCE(SUM(ip.quantidade), 0)::int AS total_vendido,
                    COALESCE(COUNT(DISTINCT p.id), 0)::int AS total_pedidos,
                    MAX(p.data_criacao) AS ultimo_pedido
                FROM livro l
                LEFT JOIN item_pedido ip ON ip.livro_id = l.id
                LEFT JOIN pedido p ON p.id = ip.pedido_id
                WHERE l.status = 'ATIVO'
                GROUP BY l.id
            ),
            autores AS (
                SELECT
                    la.livro_id,
                    STRING_AGG(DISTINCT a.nome, ', ' ORDER BY a.nome) AS autores
                FROM livro_autor la
                JOIN autor a ON a.id = la.autor_id
                GROUP BY la.livro_id
            ),
            categorias AS (
                SELECT
                    lc.livro_id,
                    STRING_AGG(DISTINCT c.nome, ', ' ORDER BY c.nome) AS categorias
                FROM livro_categoria lc
                JOIN categoria c ON c.id = lc.categoria_id
                GROUP BY lc.livro_id
            )
            SELECT
                l.titulo,
                COALESCE(l.sinopse, '') AS sinopse,
                l.valor_venda,
                COALESCE(e.quantidade, 0) AS estoque_quantidade,
                COALESCE(s.total_vendido, 0) AS total_vendido,
                COALESCE(s.total_pedidos, 0) AS total_pedidos,
                s.ultimo_pedido,
                COALESCE(autores.autores, '') AS autores,
                COALESCE(categorias.categorias, '') AS categorias
            FROM livro l
            LEFT JOIN estoque e ON e.id = l.estoque_id
            LEFT JOIN sales s ON s.livro_id = l.id
            LEFT JOIN autores ON autores.livro_id = l.id
            LEFT JOIN categorias ON categorias.livro_id = l.id
            WHERE l.status = 'ATIVO'
            ORDER BY l.titulo
        """

        with psycopg.connect(
            host=self._host,
            port=self._port,
            dbname=self._dbname,
            user=self._user,
            password=self._password,
            connect_timeout=3,
        ) as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

        candidates: list[_BookCandidate] = []
        for row in rows:
            candidates.append(
                _BookCandidate(
                    titulo=str(row["titulo"]),
                    sinopse=str(row["sinopse"] or ""),
                    valor_venda=float(row["valor_venda"]) if row["valor_venda"] is not None else None,
                    estoque_quantidade=int(row["estoque_quantidade"]) if row["estoque_quantidade"] is not None else None,
                    autores=self._split_values(row["autores"]),
                    categorias=self._split_values(row["categorias"]),
                    total_vendido=int(row["total_vendido"] or 0),
                    total_pedidos=int(row["total_pedidos"] or 0),
                    ultimo_pedido=row["ultimo_pedido"],
                )
            )

        return candidates

    def _filter_candidates(self, candidates: list[_BookCandidate], query: str) -> list[_BookCandidate]:
        """Filter candidates by query tokens and title/author/category overlap."""
        normalized_query = self._normalize(query)
        if not normalized_query:
            return candidates

        query_tokens = set(self._tokenize(normalized_query))
        matched_candidates = [
            candidate
            for candidate in candidates
            if self._candidate_matches_query(candidate, query_tokens)
        ]

        return matched_candidates or candidates

    def _build_affinity_maps(
        self,
        candidates: list[_BookCandidate],
    ) -> tuple[Counter[str], Counter[str]]:
        """Build popularity maps for authors and categories from sales history."""
        author_popularity: Counter[str] = Counter()
        category_popularity: Counter[str] = Counter()

        for candidate in candidates:
            for author in candidate.autores:
                author_popularity[author] += candidate.total_vendido
            for category in candidate.categorias:
                category_popularity[category] += candidate.total_vendido

        return author_popularity, category_popularity

    def _score_candidate(
        self,
        candidate: _BookCandidate,
        query: str,
        intent: str,
        author_popularity: Counter[str],
        category_popularity: Counter[str],
    ) -> float:
        """Score a candidate using intent, stock, sales history, and query affinity."""
        score = candidate.total_vendido * 8 + candidate.total_pedidos * 3

        if intent == "availability":
            score += 60 if self._has_stock(candidate) else -30
        elif intent == "purchase":
            score += 40 if candidate.total_vendido > 0 else -20
        else:
            score += candidate.total_vendido * 4

        if candidate.ultimo_pedido is not None:
            days_since_last_order = max((date.today() - candidate.ultimo_pedido).days, 0)
            score += max(0.0, 20.0 - (days_since_last_order / 15.0))

        score += sum(author_popularity[author] * 0.15 for author in candidate.autores)
        score += sum(category_popularity[category] * 0.1 for category in candidate.categorias)

        normalized_query = self._normalize(query)
        if not normalized_query:
            return score

        query_tokens = set(self._tokenize(normalized_query))
        score += self._token_overlap_bonus(query_tokens, candidate.titulo, 10.0)
        score += self._token_overlap_bonus(query_tokens, candidate.sinopse, 2.0)

        for author in candidate.autores:
            score += self._token_overlap_bonus(query_tokens, author, 8.0)
        for category in candidate.categorias:
            score += self._token_overlap_bonus(query_tokens, category, 6.0)

        return score

    def _format_snippet(self, candidate: _BookCandidate, *, intent: str) -> str:
        """Format a short snippet tailored to the detected user intent."""
        parts = [candidate.titulo]

        if candidate.autores:
            parts.append(f"Autores: {', '.join(candidate.autores)}")

        if candidate.categorias:
            parts.append(f"Categorias: {', '.join(candidate.categorias)}")

        if intent == "availability":
            stock_text = self._format_stock(candidate)
            parts.append(f"Estoque: {stock_text}")
            parts.append("Disponibilidade: " + ("sim" if self._has_stock(candidate) else "não"))
        elif intent == "purchase":
            if candidate.total_vendido > 0:
                parts.append(f"Histórico de compra: sim, vendido {candidate.total_vendido} vez(es) em {candidate.total_pedidos} pedido(s)")
            else:
                parts.append("Histórico de compra: sem registro de venda no banco")
        else:
            sales_info = f"{candidate.total_vendido} unidade(s) vendida(s) em {candidate.total_pedidos} pedido(s)"
            parts.append(f"Histórico: {sales_info}")

        if candidate.sinopse:
            parts.append(f"Sinopse: {self._truncate(candidate.sinopse, 110)}")
        return " | ".join(parts)

    @staticmethod
    def _detect_intent(query: str) -> str:
        """Detect whether the user asks for availability, purchase history, or recommendations."""
        normalized_query = PostgresRagGateway._normalize(query)
        if not normalized_query:
            return "recommendation"

        availability_patterns = (
            r"\bvoce tem\b",
            r"\btem esse livro\b",
            r"\btem o livro\b",
            r"\bestoque\b",
            r"\bdisponivel\b",
        )
        purchase_patterns = (
            r"\beu ja comprei\b",
            r"\bja comprei\b",
            r"\bcomprei o livro\b",
        )

        if any(re.search(pattern, normalized_query) for pattern in availability_patterns):
            return "availability"
        if any(re.search(pattern, normalized_query) for pattern in purchase_patterns):
            return "purchase"
        return "recommendation"

    @staticmethod
    def _candidate_matches_query(candidate: _BookCandidate, query_tokens: set[str]) -> bool:
        """Check whether the query mentions the candidate title, authors, or categories."""
        field_tokens = set(PostgresRagGateway._tokenize(PostgresRagGateway._normalize(candidate.titulo)))
        for author in candidate.autores:
            field_tokens.update(PostgresRagGateway._tokenize(PostgresRagGateway._normalize(author)))
        for category in candidate.categorias:
            field_tokens.update(PostgresRagGateway._tokenize(PostgresRagGateway._normalize(category)))

        return bool(query_tokens & field_tokens)

    @staticmethod
    def _has_stock(candidate: _BookCandidate) -> bool:
        """Return whether the book is currently available in stock."""
        return (candidate.estoque_quantidade or 0) > 0

    @staticmethod
    def _format_stock(candidate: _BookCandidate) -> str:
        """Format stock information for prompt snippets."""
        if candidate.estoque_quantidade is None:
            return "estoque não informado"
        if candidate.estoque_quantidade <= 0:
            return "sem unidades disponíveis"
        return f"{candidate.estoque_quantidade} unidade(s) disponível(is)"

    @staticmethod
    def _split_values(raw_value: Any) -> tuple[str, ...]:
        """Split a comma-separated SQL aggregate into a tuple of values."""
        if not raw_value:
            return ()
        return tuple(part.strip() for part in str(raw_value).split(",") if part.strip())

    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        """Truncate text while keeping snippets concise."""
        clean_text = " ".join(text.split())
        if len(clean_text) <= limit:
            return clean_text
        return clean_text[: limit - 1].rstrip() + "…"

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for accent-insensitive comparisons."""
        decomposed = unicodedata.normalize("NFKD", text)
        without_marks = "".join(character for character in decomposed if not unicodedata.combining(character))
        return re.sub(r"\s+", " ", without_marks.lower()).strip()

    @classmethod
    def _tokenize(cls, text: str) -> list[str]:
        """Extract word tokens from normalized text."""
        return re.findall(r"[a-z0-9]+", text)

    @classmethod
    def _token_overlap_bonus(cls, query_tokens: set[str], field_value: str, weight: float) -> float:
        """Compute a bonus based on overlap between query and a field value."""
        field_tokens = set(cls._tokenize(cls._normalize(field_value)))
        return len(query_tokens & field_tokens) * weight
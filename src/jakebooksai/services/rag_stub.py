"""Temporary in-memory RAG gateway used by the frontend stage."""

from __future__ import annotations

from .contracts import RagGateway


class InMemoryRagGateway(RagGateway):
    """Simple retrieval stub to preserve future backend boundary."""

    def __init__(self) -> None:
        self._knowledge_base = [
            "JakeBooks oferece automação e inteligência para processos financeiros.",
            "A arquitetura alvo é Front -> Backend -> RAG em banco -> Gemini via API gateway.",
            "Nesta fase o frontend conversa com o módulo de LLM sem backend HTTP intermediário.",
        ]

    def retrieve(self, query: str) -> list[str]:
        """Return static snippets until the real retrieval layer is implemented."""
        _ = query
        return self._knowledge_base

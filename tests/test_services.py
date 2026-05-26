"""Unit tests for the chat controller and Postgres RAG gateway."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jakebooksai.services.chat_controller import ChatController
from jakebooksai.services.contracts import ChatGateway, RagGateway
from jakebooksai.services.postgres_rag_gateway import PostgresRagGateway, _BookCandidate


class _RecordingChatGateway(ChatGateway):
    def __init__(self) -> None:
        self.last_prompt: str | None = None

    def send(self, message: str) -> str:
        self.last_prompt = message
        return message


class _StaticRagGateway(RagGateway):
    def retrieve(self, query: str) -> list[str]:
        _ = query
        return [
            "Dom Casmurro | Autores: Machado de Assis | Categorias: Romance | Histórico: 8 unidade(s) vendida(s) em 4 pedido(s)",
        ]


class _TestPostgresGateway(PostgresRagGateway):
    def _load_candidates(self) -> list[_BookCandidate]:
        return [
            _BookCandidate(
                "Dom Casmurro",
                "Romance clássico de Machado de Assis",
                10.0,
                5,
                ("Machado de Assis",),
                ("Romance",),
                8,
                4,
                date(2024, 5, 25),
            ),
            _BookCandidate(
                "Quincas Borba",
                "Romance de Machado de Assis",
                48.5,
                0,
                ("Machado de Assis",),
                ("Romance",),
                6,
                3,
                date(2024, 5, 8),
            ),
            _BookCandidate(
                "Sentimento do Mundo",
                "Coletânea de poesias de Drummond",
                35.7,
                2,
                ("Carlos Drummond de Andrade",),
                ("Poesia",),
                2,
                1,
                date(2024, 3, 18),
            ),
        ]


class ServicesTestCase(unittest.TestCase):
    def test_controller_embeds_retrieved_context_in_prompt(self) -> None:
        chat_gateway = _RecordingChatGateway()
        controller = ChatController(chat_gateway=chat_gateway, rag_gateway=_StaticRagGateway())

        response = controller.reply("Quero livros parecidos com Dom Casmurro")

        self.assertIsNotNone(chat_gateway.last_prompt)
        self.assertIn("Contexto recuperado do banco", response)
        self.assertIn("Dom Casmurro", response)

    def test_postgres_gateway_prioritizes_relevant_recommendations(self) -> None:
        gateway = _TestPostgresGateway("localhost", 5432, "jakebooks", "postgres", "postgres")

        items = gateway.retrieve("quero livros de machado de assis")

        self.assertGreaterEqual(len(items), 2)
        self.assertTrue(items[0].startswith("Dom Casmurro"))
        self.assertTrue(any("Quincas Borba" in item for item in items))

    def test_postgres_gateway_reports_stock_availability(self) -> None:
        gateway = _TestPostgresGateway("localhost", 5432, "jakebooks", "postgres", "postgres")

        items = gateway.retrieve("voce tem esse livro Dom Casmurro?")

        self.assertTrue(items[0].startswith("Dom Casmurro"))
        self.assertIn("Estoque:", items[0])
        self.assertIn("Disponibilidade: sim", items[0])

    def test_postgres_gateway_reports_purchase_history(self) -> None:
        gateway = _TestPostgresGateway("localhost", 5432, "jakebooks", "postgres", "postgres")

        items = gateway.retrieve("eu ja comprei o livro Quincas Borba?")

        self.assertTrue(items[0].startswith("Quincas Borba"))
        self.assertIn("Histórico de compra:", items[0])


if __name__ == "__main__":
    unittest.main()
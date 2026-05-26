"""Chat controller that orchestrates retrieval and LLM generation."""

from __future__ import annotations

from .contracts import ChatGateway, RagGateway


class ChatController:
    """Application service boundary for chat interactions."""

    def __init__(self, chat_gateway: ChatGateway, rag_gateway: RagGateway) -> None:
        self._chat_gateway = chat_gateway
        self._rag_gateway = rag_gateway

    def reply(self, user_message: str) -> str:
        """Generate a response for the user message."""
        clean_message = user_message.strip()
        if not clean_message:
            return "Escreva uma mensagem para iniciar a conversa."

        context_snippets = self._rag_gateway.retrieve(clean_message)
        prompt = self._compose_prompt(clean_message, context_snippets)
        return self._chat_gateway.send(prompt)

    @staticmethod
    def _compose_prompt(user_message: str, context_snippets: list[str]) -> str:
        """Build a single prompt from user text and retrieval context."""
        context_block = (
            "\n".join(f"- {snippet}" for snippet in context_snippets)
            if context_snippets
            else "- Nenhuma recomendação recuperada do banco de dados no momento."
        )
        return (
            "Você é o assistente da JakeBooks. Responda em português do Brasil, "
            "com objetividade e foco em catálogo, estoque, histórico de compras e recomendações. "
            "Use apenas os fatos recuperados e não invente títulos ou quantidades. "
            "Se o usuário perguntar se ele pessoalmente comprou um livro, deixe claro quando o sistema só tiver histórico geral do catálogo.\n\n"
            f"Contexto recuperado do banco:\n{context_block}\n\n"
            f"Pergunta do usuário: {user_message}"
        )

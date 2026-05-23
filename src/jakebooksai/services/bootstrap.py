"""Factory helpers for wiring chat services in the frontend runtime."""

from __future__ import annotations

from dataclasses import dataclass

from ..config.settings import AppSettings
from .chat_controller import ChatController
from .contracts import ChatGateway
from .gemini_gateway import GeminiChatGateway
from .rag_stub import InMemoryRagGateway


class OfflineChatGateway(ChatGateway):
    """Fallback gateway used when Gemini credentials are missing."""

    def send(self, message: str) -> str:
        _ = message
        return (
            "Integração Gemini indisponível: defina GOOGLE_API_KEY para habilitar "
            "respostas reais no chat."
        )


@dataclass(frozen=True, slots=True)
class ChatRuntime:
    """Container for runtime chat dependencies and status metadata."""

    controller: ChatController
    status_label: str
    status_description: str


def build_chat_runtime(settings: AppSettings) -> ChatRuntime:
    """Build the chat runtime components according to current settings."""
    rag_gateway = InMemoryRagGateway()

    if settings.gemini_api_key:
        chat_gateway: ChatGateway = GeminiChatGateway(
            model=settings.default_model,
            api_key=settings.gemini_api_key,
            temperature=settings.gemini_temperature,
        )
        return ChatRuntime(
            controller=ChatController(chat_gateway=chat_gateway, rag_gateway=rag_gateway),
            status_label="Gemini conectado",
            status_description="Chamadas reais via langchain-google-genai.",
        )

    chat_gateway = OfflineChatGateway()
    return ChatRuntime(
        controller=ChatController(chat_gateway=chat_gateway, rag_gateway=rag_gateway),
        status_label="Gemini não configurado",
        status_description="Defina GOOGLE_API_KEY para habilitar o modelo.",
    )

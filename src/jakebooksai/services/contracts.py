"""Abstract service contracts for the application boundary."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ChatGateway(ABC):
    """Contract for sending chat messages to the backend layer."""

    @abstractmethod
    def send(self, message: str) -> str:
        """Send a user message and return the backend response."""


class RagGateway(ABC):
    """Contract for retrieval against the RAG layer."""

    @abstractmethod
    def retrieve(self, query: str) -> list[str]:
        """Return retrieval snippets for the given query."""

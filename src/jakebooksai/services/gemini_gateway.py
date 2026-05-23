"""Gemini gateway implementation using LangChain."""

from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI

from .contracts import ChatGateway


class GeminiChatGateway(ChatGateway):
    """Gateway that sends chat prompts to Google Gemini."""

    def __init__(self, model: str, api_key: str, temperature: float) -> None:
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não configurada para chamada ao Gemini.")

        self._llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature,
        )

    def send(self, message: str) -> str:
        """Send a prompt to Gemini and normalize the text output."""
        response = self._llm.invoke(message)
        content = response.content

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            text_parts: list[str] = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and isinstance(part.get("text"), str):
                    text_parts.append(part["text"])
            return "\n".join(text_parts).strip()

        return str(content)

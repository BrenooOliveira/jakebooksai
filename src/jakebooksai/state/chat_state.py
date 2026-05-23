"""Session state helpers for the chat interface."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from ..config.settings import AppSettings


@dataclass(frozen=True, slots=True)
class ChatStatus:
    """Small status payload shown in the UI."""

    label: str
    description: str


def ensure_session_state(settings: AppSettings) -> None:
    """Initialize the Streamlit session state used by the chat screen."""
    st.session_state.setdefault("chat_messages", [])
    st.session_state.setdefault("composer_value", "")
    st.session_state.setdefault(
        "chat_status",
        ChatStatus(
            label="Backend pendente",
            description=f"A interface está pronta para integrar com {settings.backend_url}.",
        ),
    )

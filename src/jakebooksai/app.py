"""Main Streamlit application for JakeBooks AI."""

from __future__ import annotations

import streamlit as st

from .config.settings import AppSettings, load_settings
from .services.bootstrap import ChatRuntime, build_chat_runtime
from .state.chat_state import ChatStatus, ensure_session_state
from .ui.components import render_chat_shell, render_sidebar, render_top_banner
from .ui.styles import inject_styles


@st.cache_resource(show_spinner=False)
def _load_chat_runtime(settings: AppSettings) -> ChatRuntime:
    """Cache chat runtime to avoid rebuilding the LLM client on each rerun."""
    return build_chat_runtime(settings)


def run_app() -> None:
    """Render the Streamlit application."""
    settings = load_settings()
    chat_runtime = _load_chat_runtime(settings)

    st.set_page_config(
        page_title=settings.app_name,
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()
    ensure_session_state(settings)
    st.session_state.chat_status = ChatStatus(
        label=chat_runtime.status_label,
        description=chat_runtime.status_description,
    )
    render_sidebar(settings)

    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    render_top_banner(settings)
    render_chat_shell(settings, send_message=chat_runtime.controller.reply)
    st.markdown("</div>", unsafe_allow_html=True)

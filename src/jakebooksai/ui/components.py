"""Reusable UI components for the Streamlit frontend."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from ..config.settings import AppSettings


def render_sidebar(settings: AppSettings) -> None:
    """Render the navigation and project status in the sidebar."""
    status = st.session_state.chat_status

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-card">
                <p class="sidebar-heading">JakeBooks AI</p>
                <p class="sidebar-text">
                    Frontend Streamlit preparado para crescer em camadas.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-card">
                <p class="sidebar-heading">Status atual</p>
                <p class="sidebar-text"><strong>{status.label}</strong></p>
                <p class="sidebar-text">{status.description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-card">
                <p class="sidebar-heading">Configuração</p>
                <p class="sidebar-text">Ambiente: <strong>{settings.environment}</strong></p>
                <p class="sidebar-text">Modelo padrão: <strong>{settings.default_model}</strong></p>
                <p class="sidebar-text">Backend futuro: <strong>{settings.backend_url}</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-card">
                <p class="sidebar-heading">Futuras camadas</p>
                <ul class="sidebar-list">
                    <li>Frontend Streamlit</li>
                    <li>Backend de aplicação</li>
                    <li>RAG com banco de dados</li>
                    <li>Gemini via API gateway</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_top_banner(settings: AppSettings) -> None:
    """Render the top banner for the main content area."""
    status = st.session_state.chat_status

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">Frontend em construção</div>
            <h1 class="hero-title">{settings.app_name}</h1>
            <p class="hero-subtitle">{settings.tagline}</p>
            <div class="status-row">
                <span class="status-pill">{status.label}</span>
                <span class="status-pill">Arquitetura preparada para backend futuro</span>
                <span class="status-pill">Streamlit como interface principal</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_shell(settings: AppSettings, send_message: Callable[[str], str]) -> None:
    """Render chat history and execute message exchange through service boundary."""
    st.markdown(
        """
        <div class="panel-card">
            <p class="panel-title">Janela de conversa</p>
            <p class="panel-text">
                A interface conversa com um controller de aplicação,
                preservando a fronteira para o backend futuro.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input(f"Converse com {settings.app_name}.")
    if not user_prompt:
        return

    st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando módulo LLM..."):
            try:
                assistant_reply = send_message(user_prompt)
            except Exception as error:
                assistant_reply = (
                    "Falha ao consultar o serviço de LLM. "
                    f"Detalhe técnico: {error}"
                )
            st.markdown(assistant_reply)

    st.session_state.chat_messages.append(
        {"role": "assistant", "content": assistant_reply}
    )

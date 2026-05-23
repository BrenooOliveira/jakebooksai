"""Custom visual styling for the Streamlit app."""

from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    """Inject the app's visual styling."""
    st.markdown(
        """
        <style>
            :root {
                color-scheme: dark;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(251, 146, 60, 0.18), transparent 28%),
                    radial-gradient(circle at top right, rgba(56, 189, 248, 0.14), transparent 24%),
                    linear-gradient(180deg, #07111f 0%, #0b1220 40%, #111827 100%);
            }

            .app-shell {
                max-width: 1120px;
                margin: 0 auto;
                padding: 0.5rem 0 1.5rem;
            }

            .hero-card,
            .panel-card,
            .sidebar-card {
                border: 1px solid rgba(148, 163, 184, 0.18);
                background: rgba(15, 23, 42, 0.72);
                backdrop-filter: blur(14px);
                border-radius: 24px;
                box-shadow: 0 24px 80px rgba(2, 6, 23, 0.34);
            }

            .hero-card {
                padding: 1.75rem 1.75rem 1.5rem;
                margin-bottom: 1rem;
            }

            .eyebrow {
                color: #f59e0b;
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }

            .hero-title {
                color: #f8fafc;
                font-size: 2.2rem;
                font-weight: 800;
                line-height: 1.05;
                margin: 0;
            }

            .hero-subtitle {
                color: #cbd5e1;
                font-size: 1rem;
                line-height: 1.55;
                margin: 0.9rem 0 0;
                max-width: 68ch;
            }

            .status-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
                margin-top: 1rem;
            }

            .status-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                border-radius: 999px;
                border: 1px solid rgba(148, 163, 184, 0.2);
                background: rgba(30, 41, 59, 0.8);
                color: #e2e8f0;
                padding: 0.45rem 0.85rem;
                font-size: 0.86rem;
            }

            .panel-card {
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .panel-title {
                color: #f8fafc;
                font-size: 1.1rem;
                font-weight: 700;
                margin: 0 0 0.5rem;
            }

            .panel-text {
                color: #cbd5e1;
                line-height: 1.55;
                margin: 0;
            }

            .sidebar-card {
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .sidebar-heading {
                color: #f8fafc;
                font-size: 1rem;
                font-weight: 700;
                margin: 0 0 0.45rem;
            }

            .sidebar-text {
                color: #cbd5e1;
                line-height: 1.5;
                margin: 0;
            }

            .sidebar-list {
                color: #cbd5e1;
                line-height: 1.6;
                padding-left: 1.1rem;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.88));
                border-right: 1px solid rgba(148, 163, 184, 0.12);
            }

            .stChatInput {
                opacity: 0.92;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

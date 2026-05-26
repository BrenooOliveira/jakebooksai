"""Application settings loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Runtime settings for the frontend."""

    app_name: str
    tagline: str
    backend_url: str
    default_model: str
    environment: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    gemini_api_key: str
    gemini_temperature: float


def load_settings() -> AppSettings:
    """Load the current app settings from environment variables."""
    return AppSettings(
        app_name=os.getenv("JAKEBOOKS_APP_NAME", "JakeBooks AI"),
        tagline=os.getenv(
            "JAKEBOOKS_APP_TAGLINE",
            "Interface de chat pronta para receber o backend em camadas.",
        ),
        backend_url=os.getenv("JAKEBOOKS_BACKEND_URL", "http://localhost:8000"),
        default_model=os.getenv("JAKEBOOKS_DEFAULT_MODEL", "gemini-2.5-flash-lite"),
        environment=os.getenv("JAKEBOOKS_ENVIRONMENT", "development"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "jakebooks"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "postgres"),
        gemini_api_key=os.getenv("GOOGLE_API_KEY", ""),
        gemini_temperature=float(os.getenv("JAKEBOOKS_GEMINI_TEMPERATURE", "0.2")),
    )

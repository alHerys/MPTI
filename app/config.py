"""Application settings loaded from environment variables."""
import os


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "sqlite:///./coldstart.db")
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


def is_production() -> bool:
    return os.environ.get("APP_ENV", "development") == "production"


def secret_key() -> str:
    return os.environ.get("SECRET_KEY", "")


def demo_user() -> str:
    return os.environ.get("DEMO_USER", "demo")


def demo_password() -> str:
    return os.environ.get("DEMO_PASSWORD", "demo123")


def validate_production_settings() -> None:
    """Refuse to start in production with unsafe defaults."""
    if not is_production():
        return
    if not secret_key():
        raise RuntimeError("SECRET_KEY wajib diisi saat APP_ENV=production.")
    if demo_password() == "demo123":
        raise RuntimeError("DEMO_PASSWORD default tidak boleh dipakai di production.")

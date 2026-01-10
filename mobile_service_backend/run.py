import os

from app import app


def _set_default_env(var_name: str, default_value: str) -> None:
    """Set an environment variable only if it is not already defined."""
    if os.getenv(var_name) is None or os.getenv(var_name) == "":
        os.environ[var_name] = default_value


def _database_url_for_log() -> str:
    """
    Return the effective DB URL that will be used (for a startup log message).

    This mirrors app.db._build_database_url() logic without importing internal functions.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    sqlite_path = os.getenv("SQLITE_PATH", "app.db")
    return f"sqlite:///{sqlite_path}"


if __name__ == "__main__":
    # Enforce requested safe defaults (while allowing orchestrator/env to override).
    _set_default_env("DATABASE_URL", "sqlite:///app.db")
    _set_default_env("JWT_SECRET", "mobilecare_secret")
    _set_default_env("HOST", "0.0.0.0")
    _set_default_env("PORT", "3001")
    _set_default_env("BACKEND_HEALTHCHECK_DISABLED", "true")

    # Allow preview/orchestrator to inject host/port, but keep safe defaults.
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3001"))

    # IMPORTANT: Do not enable debug auto-reload for preview stability.
    # (Werkzeug reloader can spawn extra processes and confuse readiness.)
    print(
        f"[startup] Mobile Service Backend starting on {host}:{port} "
        f"using DATABASE_URL={_database_url_for_log()} "
        f"(BACKEND_HEALTHCHECK_DISABLED={os.getenv('BACKEND_HEALTHCHECK_DISABLED')})"
    )

    app.run(host=host, port=port, debug=False, use_reloader=False)

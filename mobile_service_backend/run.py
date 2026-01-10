import os

from app import app


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
    # Allow preview/orchestrator to inject host/port, but keep safe defaults.
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3001"))

    # IMPORTANT: Do not enable debug auto-reload for preview stability.
    # (Werkzeug reloader can spawn extra processes and confuse readiness.)
    print(f"[startup] Mobile Service Backend starting on {host}:{port} using DATABASE_URL={_database_url_for_log()}")

    app.run(host=host, port=port, debug=False, use_reloader=False)

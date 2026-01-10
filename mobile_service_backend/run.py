import os

from app import app

if __name__ == "__main__":
    # Allow preview/orchestrator to inject host/port, but keep safe defaults.
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3001"))
    app.run(host=host, port=port, debug=True)

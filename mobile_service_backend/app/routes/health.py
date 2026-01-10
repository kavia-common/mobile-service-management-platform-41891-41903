import os

from flask.views import MethodView
from flask_smorest import Blueprint

blp = Blueprint("Health Check", "health check", url_prefix="/", description="Health check routes")


def _healthcheck_disabled() -> bool:
    """
    Determine if health checks are disabled.

    BACKEND_HEALTHCHECK_DISABLED is a backend-local toggle used to make readiness endpoints
    return immediately OK. This is useful when preview orchestration/health gating could hang.
    """
    return os.getenv("BACKEND_HEALTHCHECK_DISABLED", "false").strip().lower() in {"1", "true", "yes"}


@blp.route("/")
class RootHealth(MethodView):
    def get(self):
        """Basic health response at root (always fast)."""
        # If disabled, still return OK immediately; no external dependency checks.
        if _healthcheck_disabled():
            return {"message": "Healthy", "healthcheck_disabled": True}
        return {"message": "Healthy"}


@blp.route("/health")
class Health(MethodView):
    def get(self):
        """Quick readiness endpoint for preview orchestration/monitoring (always fast)."""
        # Never do DB/network checks here. If disabled, make it explicit.
        if _healthcheck_disabled():
            return {"status": "ok", "healthcheck_disabled": True}
        return {"status": "ok"}

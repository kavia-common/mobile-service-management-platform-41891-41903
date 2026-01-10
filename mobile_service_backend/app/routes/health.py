from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint("Health Check", "health check", url_prefix="/", description="Health check routes")


@blp.route("/")
class RootHealth(MethodView):
    def get(self):
        """Basic health response at root."""
        return {"message": "Healthy"}


@blp.route("/health")
class Health(MethodView):
    def get(self):
        """Quick readiness endpoint for preview orchestration/monitoring."""
        return {"status": "ok"}

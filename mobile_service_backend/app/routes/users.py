from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..auth import decode_token
from ..db import get_db_session
from ..models import User
from ..schemas import UserPublicSchema


blp = Blueprint("Users", "users", url_prefix="/api/users", description="User administration")


def _require_admin() -> None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        abort(401, message="Missing Authorization: Bearer token")
    token = auth[len("Bearer ") :].strip()
    try:
        claims = decode_token(token)
    except Exception:
        abort(401, message="Invalid or expired token")
    if claims.get("role") != "admin":
        abort(403, message="Admin role required")


@blp.route("")
class UsersCollection(MethodView):
    @blp.response(200, UserPublicSchema(many=True))
    def get(self):
        """List all users (admin only)."""
        _require_admin()
        session = get_db_session()
        users = session.query(User).order_by(User.id.desc()).all()
        return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role} for u in users]

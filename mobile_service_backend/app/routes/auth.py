from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..auth import hash_password, verify_password, create_access_token, decode_token
from ..db import get_db_session
from ..models import User
from ..schemas import SignupSchema, LoginSchema, AuthTokenSchema, UserPublicSchema


blp = Blueprint("Auth", "auth", url_prefix="/api/auth", description="Authentication and identity")


def _bearer_token() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[len("Bearer ") :].strip()
    return None


def _current_user(session):
    token = _bearer_token()
    if not token:
        abort(401, message="Missing Authorization: Bearer token")
    try:
        claims = decode_token(token)
    except Exception:
        abort(401, message="Invalid or expired token")

    user_id = int(claims.get("sub"))
    user = session.get(User, user_id)
    if not user:
        abort(401, message="User not found")
    return user


@blp.route("/signup")
class Signup(MethodView):
    @blp.arguments(SignupSchema)
    @blp.response(200, AuthTokenSchema)
    def post(self, payload):
        """Create a user account and return a JWT access token."""
        session = get_db_session()
        existing = session.query(User).filter(User.email == payload["email"].lower()).first()
        if existing:
            abort(409, message="Email already registered")

        user = User(
            email=payload["email"].lower(),
            full_name=payload["full_name"],
            password_hash=hash_password(payload["password"]),
            role="customer",
        )
        session.add(user)
        session.commit()

        token = create_access_token(user_id=user.id, email=user.email, role=user.role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role},
        }


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(LoginSchema)
    @blp.response(200, AuthTokenSchema)
    def post(self, payload):
        """Authenticate a user and return a JWT access token."""
        session = get_db_session()
        user = session.query(User).filter(User.email == payload["email"].lower()).first()
        if not user or not verify_password(payload["password"], user.password_hash):
            abort(401, message="Invalid credentials")

        token = create_access_token(user_id=user.id, email=user.email, role=user.role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role},
        }


@blp.route("/me")
class Me(MethodView):
    @blp.response(200, UserPublicSchema)
    def get(self):
        """Return the authenticated user's profile."""
        session = get_db_session()
        user = _current_user(session)
        return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}

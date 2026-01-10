import os
from datetime import datetime, timedelta, timezone
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

DEFAULT_TOKEN_TTL_MINUTES = 60 * 24  # 24h


def _jwt_secret() -> str:
    """
    Return the JWT signing secret.

    For local development/preview we allow a sane default to avoid startup failures.
    IMPORTANT: Override JWT_SECRET in any real deployment.
    """
    secret = os.getenv("JWT_SECRET", "mobilecare_secret")
    return secret


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a plaintext password using Werkzeug's recommended hashing scheme."""
    return generate_password_hash(password)


# PUBLIC_INTERFACE
def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return check_password_hash(password_hash, password)


# PUBLIC_INTERFACE
def create_access_token(user_id: int, email: str, role: str, ttl_minutes: int | None = None) -> str:
    """Create a signed JWT access token for the given user."""
    now = datetime.now(timezone.utc)
    ttl = ttl_minutes if ttl_minutes is not None else int(os.getenv("JWT_TTL_MINUTES", DEFAULT_TOKEN_TTL_MINUTES))
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl)).timestamp()),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


# PUBLIC_INTERFACE
def decode_token(token: str) -> dict:
    """Decode and validate JWT token, raising jwt exceptions if invalid."""
    return jwt.decode(token, _jwt_secret(), algorithms=["HS256"])

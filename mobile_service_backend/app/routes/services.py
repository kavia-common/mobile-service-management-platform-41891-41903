from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..auth import decode_token
from ..db import get_db_session
from ..models import Service
from ..schemas import ServiceSchema, ServiceCreateSchema


blp = Blueprint("Services", "services", url_prefix="/api/services", description="Browse and manage services")


def _claims_or_401() -> dict:
    """Extract and validate JWT claims from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        abort(401, message="Missing Authorization: Bearer token")
    token = auth[len("Bearer ") :].strip()
    try:
        return decode_token(token)
    except Exception:
        abort(401, message="Invalid or expired token")


def _require_admin() -> dict:
    """Require that the current request is authenticated as an admin."""
    claims = _claims_or_401()
    if claims.get("role") != "admin":
        abort(403, message="Admin role required")
    return claims


@blp.route("")
class ServicesCollection(MethodView):
    @blp.response(200, ServiceSchema(many=True))
    def get(self):
        """
        List services (public).

        Query params:
        - q: free-text search across name/category/description
        - category: exact category filter
        - min_price_cents, max_price_cents: integer range filter
        - include_inactive: if true, returns inactive services too (admin only)
        """
        session = get_db_session()

        q_text = (request.args.get("q") or "").strip()
        category = (request.args.get("category") or "").strip()

        include_inactive = (request.args.get("include_inactive") or "false").strip().lower() in {"1", "true", "yes"}
        if include_inactive:
            # Must be admin to see inactive services.
            _require_admin()

        min_price = request.args.get("min_price_cents")
        max_price = request.args.get("max_price_cents")

        query = session.query(Service)

        if not include_inactive:
            query = query.filter(Service.is_active == 1)

        if category:
            query = query.filter(Service.category == category)

        # Basic search/filter without relying on DB-specific full text features.
        # Works with SQLite and most SQL engines.
        if q_text:
            like = f"%{q_text}%"
            query = query.filter(
                (Service.name.ilike(like)) | (Service.category.ilike(like)) | (Service.description.ilike(like))
            )

        if min_price is not None and min_price != "":
            try:
                query = query.filter(Service.price_cents >= int(min_price))
            except ValueError:
                abort(400, message="min_price_cents must be an integer")

        if max_price is not None and max_price != "":
            try:
                query = query.filter(Service.price_cents <= int(max_price))
            except ValueError:
                abort(400, message="max_price_cents must be an integer")

        services = query.order_by(Service.id.desc()).all()
        return services

    @blp.arguments(ServiceCreateSchema)
    @blp.response(201, ServiceSchema)
    def post(self, payload):
        """Create a service (admin only)."""
        _require_admin()
        session = get_db_session()
        service = Service(
            name=payload["name"],
            category=payload["category"],
            description=payload["description"],
            price_cents=payload["price_cents"],
            duration_minutes=payload["duration_minutes"],
            is_active=1,
        )
        session.add(service)
        session.commit()
        return service


@blp.route("/<int:service_id>")
class ServiceItem(MethodView):
    @blp.response(200, ServiceSchema)
    def get(self, service_id: int):
        """Get a single active service (public)."""
        session = get_db_session()
        service = session.get(Service, service_id)
        if not service or service.is_active != 1:
            abort(404, message="Service not found")
        return service

    @blp.arguments(ServiceCreateSchema(partial=True))
    @blp.response(200, ServiceSchema)
    def patch(self, payload, service_id: int):
        """Update a service (admin only)."""
        _require_admin()
        session = get_db_session()
        service = session.get(Service, service_id)
        if not service:
            abort(404, message="Service not found")

        for k, v in payload.items():
            setattr(service, k, v)
        session.commit()
        return service

    @blp.response(200)
    def delete(self, service_id: int):
        """
        Delete a service (admin only).

        For safety in early iterations, this performs a soft delete by setting is_active=0.
        """
        _require_admin()
        session = get_db_session()
        service = session.get(Service, service_id)
        if not service:
            abort(404, message="Service not found")

        service.is_active = 0
        session.commit()
        return {"ok": True, "message": "Service deactivated"}

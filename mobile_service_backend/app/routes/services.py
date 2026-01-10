from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..auth import decode_token
from ..db import get_db_session
from ..models import Service
from ..schemas import ServiceSchema, ServiceCreateSchema


blp = Blueprint("Services", "services", url_prefix="/api/services", description="Browse and manage services")


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
class ServicesCollection(MethodView):
    @blp.response(200, ServiceSchema(many=True))
    def get(self):
        """List active services (public)."""
        session = get_db_session()
        services = session.query(Service).filter(Service.is_active == 1).order_by(Service.id.desc()).all()
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
        """Get a single service (public)."""
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

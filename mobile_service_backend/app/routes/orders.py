from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..auth import decode_token
from ..db import get_db_session
from ..models import Order, Service, User
from ..schemas import OrderSchema, OrderCreateSchema, OrderUpdateSchema


blp = Blueprint("Orders", "orders", url_prefix="/api/orders", description="Create and manage service orders")


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


def _is_admin(claims: dict) -> bool:
    """Return True if claims represent an admin."""
    return claims.get("role") == "admin"


@blp.route("")
class OrdersCollection(MethodView):
    @blp.response(200, OrderSchema(many=True))
    def get(self):
        """List orders for the current user (or all orders if admin)."""
        claims = _claims_or_401()
        session = get_db_session()

        q = session.query(Order).order_by(Order.id.desc())
        if not _is_admin(claims):
            q = q.filter(Order.user_id == int(claims.get("sub")))

        orders = q.all()
        # Ensure relationships are loaded for response
        for o in orders:
            _ = o.service
            _ = o.user
        return orders

    @blp.arguments(OrderCreateSchema)
    @blp.response(201, OrderSchema)
    def post(self, payload):
        """Create a new order for the current user."""
        claims = _claims_or_401()
        session = get_db_session()

        user = session.get(User, int(claims.get("sub")))
        if not user:
            abort(401, message="User not found")

        service = session.get(Service, payload["service_id"])
        if not service or service.is_active != 1:
            abort(404, message="Service not found")

        order = Order(
            user_id=user.id,
            service_id=service.id,
            status="requested",
            notes=payload.get("notes", ""),
        )
        session.add(order)
        session.commit()

        _ = order.service
        _ = order.user
        return order


@blp.route("/<int:order_id>")
class OrderItem(MethodView):
    @blp.response(200, OrderSchema)
    def get(self, order_id: int):
        """Get one order (owner or admin)."""
        claims = _claims_or_401()
        session = get_db_session()

        order = session.get(Order, order_id)
        if not order:
            abort(404, message="Order not found")

        if not _is_admin(claims) and order.user_id != int(claims.get("sub")):
            abort(403, message="Not permitted")

        _ = order.service
        _ = order.user
        return order

    @blp.arguments(OrderUpdateSchema)
    @blp.response(200, OrderSchema)
    def patch(self, payload, order_id: int):
        """Update order status/notes (admin only)."""
        claims = _claims_or_401()
        if not _is_admin(claims):
            abort(403, message="Admin role required")

        session = get_db_session()
        order = session.get(Order, order_id)
        if not order:
            abort(404, message="Order not found")

        if "status" in payload:
            order.status = payload["status"]
        if "notes" in payload:
            order.notes = payload["notes"]

        session.commit()
        _ = order.service
        _ = order.user
        return order


@blp.route("/<int:order_id>/cancel")
class OrderCancel(MethodView):
    @blp.response(200, OrderSchema)
    def post(self, order_id: int):
        """
        Cancel an order (owner or admin).

        Cancellation rules:
        - Order owner can cancel when status is requested/scheduled.
        - Admin can cancel any order at any time.
        """
        claims = _claims_or_401()
        session = get_db_session()

        order = session.get(Order, order_id)
        if not order:
            abort(404, message="Order not found")

        is_owner = order.user_id == int(claims.get("sub"))
        if not (_is_admin(claims) or is_owner):
            abort(403, message="Not permitted")

        if not _is_admin(claims) and order.status not in {"requested", "scheduled"}:
            abort(400, message="Order can no longer be cancelled")

        order.status = "cancelled"
        session.commit()
        _ = order.service
        _ = order.user
        return order

from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from werkzeug.exceptions import HTTPException

from .db import init_db, shutdown_db_session, get_db_session
from .models import Service, User
from .auth import hash_password
from .routes.health import blp as health_blp
from .routes.auth import blp as auth_blp
from .routes.services import blp as services_blp
from .routes.orders import blp as orders_blp
from .routes.users import blp as users_blp


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    The API is exposed under /api/* and OpenAPI docs are available under /docs.
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Allow the React dev server to access this API.
    # In production, restrict this to your deployed frontend origin(s).
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:3000"]}},
        supports_credentials=False,
    )

    app.config["API_TITLE"] = "Mobile Service Management API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    api = Api(app)
    api.register_blueprint(health_blp)
    api.register_blueprint(auth_blp)
    api.register_blueprint(services_blp)
    api.register_blueprint(orders_blp)
    api.register_blueprint(users_blp)

    # Database init + teardown (scoped session removal)
    init_db()
    app.teardown_appcontext(shutdown_db_session)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        """
        Return consistent JSON errors for HTTP exceptions.

        flask-smorest already returns JSON for its own aborts; this handler helps
        for any uncaught Werkzeug HTTPExceptions.
        """
        return {"error": e.name, "message": e.description}, e.code

    # Lightweight dev seed route (safe to call multiple times).
    @app.get("/api/dev/seed")
    def dev_seed():
        """
        Seed the database with a few services and an admin user for local development.

        Requires env var JWT_SECRET to be present for auth flows, but seeding itself does not require auth.
        """
        session = get_db_session()

        # Create default admin if missing
        admin_email = "admin@example.com"
        existing_admin = session.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            session.add(
                User(
                    email=admin_email,
                    full_name="Admin User",
                    password_hash=hash_password("admin123"),
                    role="admin",
                )
            )

        # Seed services if table empty
        if session.query(Service).count() == 0:
            session.add_all(
                [
                    Service(
                        name="Screen Replacement",
                        category="Repair",
                        description="Replace cracked or damaged screens with quality parts and warranty.",
                        price_cents=12900,
                        duration_minutes=90,
                        is_active=1,
                    ),
                    Service(
                        name="Battery Replacement",
                        category="Repair",
                        description="Restore battery health and improve performance with a new battery.",
                        price_cents=7900,
                        duration_minutes=45,
                        is_active=1,
                    ),
                    Service(
                        name="SIM & eSIM Setup",
                        category="Setup",
                        description="Assistance with SIM transfer, eSIM activation, and carrier settings.",
                        price_cents=2900,
                        duration_minutes=20,
                        is_active=1,
                    ),
                ]
            )

        session.commit()
        return {"ok": True, "message": "Seeded demo data (admin: admin@example.com / admin123)"}

    return app


app = create_app()
api = Api(app)

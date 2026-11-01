
"""Flask application factory for The Choice."""

import os

from dotenv import load_dotenv
from flask import Flask


def create_app() -> Flask:
    """Create and configure the Flask application."""

    load_dotenv()

    app = Flask(__name__)

    secret_key = os.getenv("FLASK_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("FLASK_SECRET_KEY is not configured.")

    app.config.update(
        SECRET_KEY=secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    from app.routes.main import main_bp

    app.register_blueprint(main_bp)

    return app

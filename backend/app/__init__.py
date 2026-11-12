import os

import click
from flask import Flask

from .config import Config
from .extensions import cors, db, limiter, migrate


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    if not app.config.get("TESTING") and app.config["SECRET_KEY"].startswith("dev-insecure"):
        app.logger.warning("SECRET_KEY is the insecure default - set a real one in .env for production.")

    db.init_app(app)
    from . import models  # noqa: F401  (register models for migrations)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
                  allow_headers=["Authorization", "Content-Type"], methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    limiter.init_app(app)
    limiter.enabled = app.config.get("RATELIMIT_ENABLED", True)

    from .routes import (admin_routes, agent_routes, ai_routes, analytics_routes, attachment_routes, auth_routes,
                         category_routes, knowledge_routes, message_routes, notification_routes, ticket_routes, user_routes)
    for m in (auth_routes, user_routes, admin_routes, agent_routes, ticket_routes, message_routes, attachment_routes,
              category_routes, knowledge_routes, notification_routes, analytics_routes, ai_routes):
        app.register_blueprint(m.bp)

    from .utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        resp.headers.setdefault("Cache-Control", "no-store")
        return resp

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok"}

    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Drop and recreate all tables first (DEV ONLY).")
    def seed_command(reset):
        """Load clearly-labelled development seed data."""
        from .seed import seed_database
        if reset:
            db.drop_all()
        db.create_all()
        click.echo(seed_database())

    return app

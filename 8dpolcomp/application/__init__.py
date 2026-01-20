
import logging
import os

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Prep db
db = SQLAlchemy()
from application.models.questions import Questions
from application.models.results import Results


def create_app(register_blueprints=True):
    """
    Create and configure the Flask application.

    Args:
        register_blueprints (bool): If True, registers all view blueprints. False for jobs.

    Returns:
        Flask: Configured Flask app instance.
    """

    app = Flask(__name__)

    app.secret_key = os.getenv("APP_SECRET_KEY") or os.urandom(12).hex()
    app.static_folder = "static"

    # Load config
    try:
        app.config.from_pyfile("./utils/config.py")
    except Exception:
        logger.exception("[create_app] Failed to load config file")
        raise

    # Cache-busting for static files
    @app.context_processor
    def _inject_versioned_url_for():
        def versioned_url_for(endpoint, **values):
            if endpoint == "static" and "v" not in values:
                values["v"] = app.config.get("STATIC_VERSION", "1")
            return url_for(endpoint, **values)

        return {"url_for": versioned_url_for}

    # Init SQLAlchemy
    try:
        db.init_app(app)
    except Exception:
        logger.exception("[create_app] Failed to init SQLAlchemy")
        raise

    # Register view blueprints
    if register_blueprints:
        with app.app_context():
            try:
                from application.views import (
                    index, instructions, test, form, results, data,
                    contact, api, ads, privacy, terms
                )
                app.register_blueprint(index.v)
                app.register_blueprint(instructions.v)
                app.register_blueprint(test.v)
                app.register_blueprint(form.v)
                app.register_blueprint(results.v)
                app.register_blueprint(data.v)
                app.register_blueprint(contact.v)
                app.register_blueprint(api.v)
                app.register_blueprint(ads.v)
                app.register_blueprint(privacy.v)
                app.register_blueprint(terms.v)
            except Exception:
                logger.exception("[create_app] Failed to register blueprints")
                raise

    return app

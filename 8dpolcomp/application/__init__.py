
import logging
import os

from flask import Flask
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

    Raises:
        RuntimeError: If config fails to load or app init fails.
    """

    # Initialise app & db
    app = Flask(__name__)

    app.secret_key = os.getenv("APP_SECRET_KEY") or os.urandom(12).hex()
    app.static_folder = "static"

    try:
        app.config.from_pyfile("./utils/config.py")
    except Exception:
        logger.exception("[create_app] Failed to load config file")
        raise

    try:
        db.init_app(app)
    except Exception:
        logger.exception("[create_app] Failed to init SQLAlchemy")
        raise

    # Register view blueprints
    if register_blueprints:
        with app.app_context():
            try:
                from application.views import index, instructions, test, form, results, data, contact, api, ads, privacy, terms
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

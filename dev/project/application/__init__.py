from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Prep db
db = SQLAlchemy()
from application.models.questions import Questions
from application.models.results import Results

def create_app():

    # Initialise app & db
    app = Flask(__name__)
    app.secret_key = os.urandom(12).hex()
    app.static_folder = "static"
    app.config.from_pyfile('../config/app_config.py')
    db.init_app(app)
    
    # Register view blueprints
    with app.app_context():
        from application.views import index, instructions, test, form, results, data, contact, api
        app.register_blueprint(index.v)
        app.register_blueprint(instructions.v)
        app.register_blueprint(test.v)
        app.register_blueprint(form.v)
        app.register_blueprint(results.v)
        app.register_blueprint(data.v)
        app.register_blueprint(contact.v)
        app.register_blueprint(api.v)

    return app

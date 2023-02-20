from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)
    app.secret_key = os.urandom(12).hex()
    app.static_folder = "static"
    app.config.from_pyfile('../config/app_config.py')

    db.init_app(app)

    with app.app_context():
        from application.views import index, instructions, test, results, data
        app.register_blueprint(index.v)
        app.register_blueprint(instructions.v)
        app.register_blueprint(test.v)
        app.register_blueprint(results.v)
        app.register_blueprint(data.v)

    return app

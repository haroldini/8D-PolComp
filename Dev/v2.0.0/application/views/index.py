from flask import Blueprint, render_template, session
import json

from application.controllers.results import ResultsController as Results

v = Blueprint('index', __name__)

@v.route("/", methods=["POST", "GET"])
def index():
    session.clear()

    recent = {
        "diplomacy": 0.1,
        "economics": -0.1,
        "government": -0.1,
        "politics": -0.1,
        "religion": 0.1,
        "society": -0.1,
        "state": 0.1,
        "technology": -0.1
    }

    data = {
        "recent": json.dumps(recent),
        "completed_count": Results.get_count()
    }
    return render_template("pages/index.html", data=data)




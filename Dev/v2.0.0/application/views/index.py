from flask import Blueprint, render_template, session
import json

from application.controllers.results import ResultsController as Results

v = Blueprint('index', __name__)

@v.route("/", methods=["POST", "GET"])
def index():
    session.clear()
    
    data = {
        "recent": Results.get_recent_results()[0].scores,
        "completed_count": Results.get_count()
    }
    return render_template("pages/index.html", data=data)




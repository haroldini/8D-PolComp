from flask import Blueprint, render_template
from application.controllers import questions

v = Blueprint('index', __name__)

@v.route("/", methods=["POST", "GET"])
def index():
    print(questions.get_all())
    data = {
        "completed_count": 100,
        "started_count": 200,
        "recorded_count": 50,
    }
    return render_template("pages/index.html", data=data)




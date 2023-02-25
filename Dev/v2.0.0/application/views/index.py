from flask import Blueprint, render_template, session

v = Blueprint('index', __name__)

@v.route("/", methods=["POST", "GET"])
def index():
    session.clear()

    data = {
        "completed_count": 100,
        "started_count": 200,
        "recorded_count": 50,
    }
    return render_template("pages/index.html", data=data)




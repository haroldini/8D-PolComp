from flask import Blueprint, render_template

v = Blueprint('index', __name__)

@v.route("/", methods=["POST", "GET"])
def index():
    return render_template("pages/index.html")
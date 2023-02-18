from flask import Blueprint, render_template

v = Blueprint('data', __name__)

@v.route("/data", methods=["POST", "GET"])
def data():
    return render_template("pages/data.html")
from flask import Blueprint, render_template

v = Blueprint('test', __name__)

@v.route("/test", methods=["POST", "GET"])
def test():
    return render_template("pages/test.html")
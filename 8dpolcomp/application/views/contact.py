from flask import Blueprint, render_template


v = Blueprint('contact', __name__)


@v.route("/contact", methods=["GET"])
def contact():  

    return render_template("pages/contact.html")




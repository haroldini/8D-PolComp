from flask import Blueprint, render_template
from application.controllers.questions import QuestionsController as Questions

v = Blueprint('data', __name__)

@v.route("/data", methods=["POST", "GET"])
def data():
    questions = Questions.get_all()
    columns = questions[0].__mapper__.column_attrs.keys()

    return render_template("pages/data.html", questions=questions, columns=columns)
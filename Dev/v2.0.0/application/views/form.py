from flask import Blueprint, render_template, session, request, redirect, url_for
import json

from application.controllers.questions import QuestionsController as Questions
from application.controllers.results import ResultsController as Results

v = Blueprint('form', __name__)


@v.route("/form", methods=["GET", "POST"])
def form():

    # Redirect to correct template.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "form":
        return redirect(url_for(f"{session['template']}.{session['template']}"))
    
    if request.method == "POST":
        data = request.get_json()

        if data["action"] == "to_results":
            demographics = data["demographics"]
            Results.add_result(
                demographics = json.dumps(demographics),
                scores = json.dumps(session["results"]),
                answers = json.dumps(session["answers"])
            )
            session["template"] = "results"
            return {"status": "success"}, 200

    # Get question texts, pass to front.
    texts = json.dumps(Questions.get_texts(test=True))

    session["template"] = "form"
    print("TEMPLATE: ", session["template"])
    return render_template(f"pages/{session['template']}.html", texts=texts)

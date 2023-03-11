from flask import Blueprint, render_template, session, request, redirect, url_for
import json

from application.controllers.questions import QuestionsController as Questions
from application.controllers.results import ResultsController as Results

v = Blueprint('test', __name__)

def validate_answers(answers):
    answers = { int(q): int(answer) for q, answer in answers.items() }
    return answers

def calculate_results(answers):
    scores = Questions.get_scores(test=True)
    r_scores = {}
    for q_id, q_scores in scores.items():
        r_scores[q_id] = { axis: q_score*answers[q_id] for axis, q_score in q_scores.items() }
    r_sums = { axis: sum([ v[axis] for v in r_scores.values() ]) for axis in r_scores[1].keys() }
    max_scores = Questions.get_max_scores()

    return { axis: round(val/max_scores[axis], 2) for axis, val in r_sums.items() }

@v.route("/test", methods=["GET", "POST"])
def test():

    # Redirect to correct template.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "test":
        return redirect(url_for(f"{session['template']}.{session['template']}"))
    
    if request.method == "POST":
        data = request.get_json()

        if data["action"] == "to_instructions":
            session["template"] = "instructions"
            return {"status": "success"}, 200

        elif data["action"] == "to_form":
            answers = validate_answers(data["answers"])
            results = calculate_results(answers)
            session["answers"] = answers
            session["results"] = results
            session["template"] = "form"
            return {"status": "success"}, 200

    # Get question texts, pass to front.
    texts = json.dumps(Questions.get_texts(test=False))

    session["template"] = "test"
    print("TEMPLATE: ", session["template"])
    return render_template(f"pages/{session['template']}.html", texts=texts)

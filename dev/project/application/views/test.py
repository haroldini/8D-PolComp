from flask import Blueprint, render_template, session, request, redirect, url_for
import json

from application.controllers.questions import QuestionsController as Questions

v = Blueprint('test', __name__)

# From dict of {question: answer, ...}, calculate results as dict of {axis: score, ...}
def calculate_results(answers):
    scores = Questions.get_scores(test=False)

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

        # Back button pressed from question 1
        if data["action"] == "to_instructions":
            session["template"] = "instructions"
            return {"status": "success"}, 200

        # Any button pressed on final question
        elif data["action"] == "to_form":
            answers = { int(q): int(answer) for q, answer in data["answers"].items() }
            results = calculate_results(answers)
            session["answers"] = answers
            session["results"] = results
            session["template"] = "form"
            return {"status": "success"}, 200

    # Get question texts, pass to front.
    texts = json.dumps(Questions.get_texts(test=False))

    session["template"] = "test"
    return render_template(f"pages/{session['template']}.html", texts=texts)
from flask import Blueprint, render_template, session, request, redirect, url_for
from application.controllers.questions import QuestionsController as Questions
import json

v = Blueprint('test', __name__)

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
            # Back button
            session["template"] = "instructions"
            return {"status": "success"}, 200
        elif data["action"] == "to_results":
            # Final question
            # Insert function to process answers and scores to results
            scores = Questions.get_scores(test=True)
            answers = data["answers"]
            session["results"] = answers
            session["template"] = "results"
            return {"status": "success"}, 200

    # Get question texts, pass to front.
    texts = json.dumps(Questions.get_texts(test=True))

    session["template"] = "test"
    print("TEMPLATE: ", session["template"])
    return render_template(f"pages/{session['template']}.html", texts=texts)

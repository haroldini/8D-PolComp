from flask import Blueprint, render_template, session, request, redirect, url_for
from application.controllers.questions import QuestionsController as Questions

v = Blueprint('results', __name__)

@v.route("/results", methods=["GET", "POST"])
def results():
    
    # Redirect to correct template.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "results":
        return redirect(url_for(f"{session['template']}.{session['template']}"))
    
    if request.method == "POST":
        data = request.get_json()
        if data["action"] == "to_instructions":
            session["template"] = "instructions"
        return {"status": "success"}, 200

    print("TEMPLATE: ", session["template"])
    return render_template(f"pages/{session['template']}.html", results=session["results"])
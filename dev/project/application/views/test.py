from flask import Blueprint, render_template, session, request, redirect, url_for
import json

from application.controllers.questions import QuestionsController as Questions


v = Blueprint('test', __name__)


@v.route("/test", methods=["GET"])
def test():

    # Redirect to correct template. Prevents user accessing incorrect test page.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "test":
        return redirect(url_for(f"{session['template']}.{session['template']}"))

    # Get question texts, pass to front.
    texts = json.dumps(Questions.get_texts(test=False))

    session["template"] = "test"
    return render_template(f"pages/{session['template']}.html", texts=texts)
from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
import json
import os


v = Blueprint('form', __name__)


@v.route("/form", methods=["GET"])
def form():

    # Redirect to correct template. Prevents user accessing incorrect test page.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "form":
        return redirect(url_for(f"{session['template']}.{session['template']}"))
    
    with open(os.path.join(current_app.config['REL_DIR'], "application/data/demographics/demographics.json"), "r", encoding="utf-8") as f:
        demo = json.load(f)
        f.close()

    session["template"] = "form"
    return render_template(f"pages/{session['template']}.html", site_key=current_app.config["RECAPTCHA_SITE_KEY"], demo=demo)

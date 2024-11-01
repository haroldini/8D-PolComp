from flask import Blueprint, render_template, session, request, redirect, url_for


v = Blueprint('instructions', __name__)


@v.route("/instructions", methods=["GET"])
def instructions():
    
    # Redirect to correct template. Prevents user accessing incorrect test page.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "instructions":
        return redirect(url_for(f"{session['template']}.{session['template']}"))
    
    # Render the appropriate template
    return render_template(f"pages/{session['template']}.html")
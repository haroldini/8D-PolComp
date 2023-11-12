from flask import Blueprint, render_template, session, request, redirect, url_for


v = Blueprint('instructions', __name__)

@v.route("/instructions", methods=["GET", "POST"])
def instructions():
    
    # Redirect to correct template.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "instructions":
        return redirect(url_for(f"{session['template']}.{session['template']}"))
    
    # Start test button clicked
    if request.method == "POST":
        data = request.get_json()
        if data["action"] == "to_test":
            session["template"] = "test"
        return {"status": "success"}, 200
    
    # Render the appropriate template
    return render_template(f"pages/{session['template']}.html")


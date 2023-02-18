from flask import Blueprint, render_template, session, request, redirect, url_for

v = Blueprint('test', __name__)

@v.route("/test")
def test():
    
    # Load instructions if current template not known
    if not "template" in session:
        session["template"] = "instructions"
    
    # Render the appropriate template
    print("TEMPLATE: ", session["template"])
    return render_template(f"pages/{session['template']}.html")


@v.route("/instructions", methods=["POST"])
def instructions():

    # Reload /test with instructions
    session["template"] = "instructions"
    return redirect(url_for(f"test.test"))


@v.route("/questions", methods=["POST"])
def questions():

    # Reload /test with questions
    session["template"] = "questions"
    return redirect(url_for(f"test.test"))

@v.route("/results", methods=["POST"])
def results():

    # Process answers - cross ref them
    answers = request.get_json()
    print(answers)

    # Reload /test with results
    session["template"] = "results"
    return redirect(url_for(f"test.test"))
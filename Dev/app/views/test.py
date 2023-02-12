from flask import Blueprint, render_template, session, request, redirect, url_for

v = Blueprint('test', __name__)

@v.route("/test")
def test():
    
    if not "template" in session:
        session["template"] = "instructions"
        
    print("TEMPLATE: ", session["template"])
    return render_template(f"pages/{session['template']}.html")


@v.route("/instructions", methods=["POST"])
def instructions():
    session["template"] = "instructions"
    print("TEMPLATE: ", session["template"])
    return redirect(url_for(f"test.test"))


@v.route("/questions", methods=["POST"])
def questions():
    session["template"] = "questions"
    print("TEMPLATE: ", session["template"])
    return redirect(url_for(f"test.test"))

@v.route("/results", methods=["POST"])
def results():

    # Process answers - cross ref them
    answers = request.get_json()
    print(answers)


    session["template"] = "results"
    print("TEMPLATE: ", session["template"])
    return redirect(url_for(f"test.test"))
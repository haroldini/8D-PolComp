from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
import requests
import json
import os

from application.controllers.results import ResultsController as Results


v = Blueprint('form', __name__)

def validate_results(demographics, scores, answers):
    print({"demographics": demographics, "scores": scores, "answers": answers})

    # Validate scores
    valid_axes = ["diplomacy", "economics", "government", "politics", "religion", "society", "state", "technology"]
    for axis, score in scores.items():
        if axis not in valid_axes:
            return None, False
        if not -1 <= score <= 1:
            return None, False

    # Validate answers
    for q_id, answer in answers.items():
        if not 0 <= int(q_id) <= 100:
            return None, False
        if not -2 <= int(answer) <= 2:
            return None, False

    # Validate demographics
    with open(f"{current_app.config['REL_DIR']}application/data/demographics/demographics.json", "r", encoding="utf-8") as f:
        demo_valid = json.load(f)
        f.close()
    for dem_key, dem_val in demographics.items():

        # Unknown demographic key = invalid
        # Empty demographic value = valid
        if not dem_key in demo_valid.keys():
            return None, f"{dem_key} is not a valid demographic"
        if dem_key != "identities" and dem_val == "":
            continue

        # For age key, cast to list of acceptable vals to integer
        if dem_key == "age":
            if dem_val == -1:
                continue
            elif dem_val in [int(age_val) for age_val in demo_valid[dem_key]]:
                continue
            return None, f"{dem_val} is not a valid {dem_key}"

        # For party key - acceptable vals are contained within countries
        elif dem_key == "party":
            acceptable_vals = []
            for country, party_list in demo_valid["party"].items():
                for party in party_list:
                    acceptable_vals.append(country+"-"+party)
           
            if dem_val in acceptable_vals:
                continue
            return None, f"{dem_val} is not a valid {dem_key}"
        
        # For identity key, just check for valid values across each identity in list
        elif dem_key == "identities": 
            if dem_val == []:
                continue
            for identity in dem_val:
                if identity == "":
                    demographics[dem_key] = []
                    continue
                if identity not in demo_valid[dem_key]:
                    return None, f"{identity} is not a valid {dem_key}"
                
        # For other keys - just check for valid values inside demo_valid for key.
        elif dem_val not in demo_valid[dem_key]:
            return None, f"{dem_val} is not a valid {dem_key}"

    return {"demographics": demographics, "scores": scores, "answers": answers}, True


@v.route("/form", methods=["GET", "POST"])
def form():

    # Redirect to correct template.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "form":
        return redirect(url_for(f"{session['template']}.{session['template']}"))
    
    # Get json from ajax post, check captcha. Render error message if failed
    if request.method == "POST":
        data = request.get_json()
        captcha_response = data["recaptcha"]
        secret_url = f"{current_app.config['RECAPTCHA_VERIFY_URL']}?secret={current_app.config['RECAPTCHA_SECRET_KEY']}&response={captcha_response}"
        verify_response = requests.post(url=secret_url).json()
        if not verify_response["success"]:
            return {"status": "Captcha Verification Failed"}, 401

        # Count answers for each question to add user data to pie
        session["answer_counts"] = {
            str(q_id): {"Strongly Agree": 0, "Agree": 0, "Neutral": 0, "Disagree": 0, "Strongly Disagree": 0} 
            for q_id in session["answers"].keys()}
        keys = {2: "Strongly Agree", 1: "Agree", 0: "Neutral", -1: "Disagree", -2: "Strongly Disagree"}
        for q_id, q_ans in session["answers"].items():
            session["answer_counts"][q_id][keys[q_ans]] += 1

        # Add user's result to database ######################################################################################################### REMOVE BEFORE PUSHING
        test = False
        if not test:
            results, valid = validate_results(
                demographics = data["demographics"],
                scores = session["results"],
                answers = session["answers"])
            if valid != True:
                return {"status": f"Result Validation Failed: {valid}. Contact developer to report issue."}, 401
            Results.add_result(results)

        # Return success, ajax will redirect to results
        session["template"] = "results"
        return {"status": "success"}, 200

    with open(os.path.join(current_app.config['REL_DIR'], "application/data/demographics/demographics.json"), "r", encoding="utf-8") as f:
        demo = json.load(f)
        f.close()

    session["template"] = "form"
    return render_template(f"pages/{session['template']}.html", site_key=current_app.config["RECAPTCHA_SITE_KEY"], demo=demo)

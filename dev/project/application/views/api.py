from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
import requests
import json
import os

from application.controllers.results import ResultsController as Results
from application.controllers.questions import QuestionsController as Questions


v = Blueprint('api', __name__)


def validate_results(demographics, scores, answers):

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


def get_answer_counts():
    session["answer_counts"] = {
        str(q_id): {"Strongly Agree": 0, "Agree": 0, "Neutral": 0, "Disagree": 0, "Strongly Disagree": 0} 
        for q_id in session["answers"].keys()}
    keys = {2: "Strongly Agree", 1: "Agree", 0: "Neutral", -1: "Disagree", -2: "Strongly Disagree"}
    for q_id, q_ans in session["answers"].items():
        session["answer_counts"][q_id][keys[q_ans]] += 1


def calculate_results(answers):
    # From dict of {question: answer, ...}, calculate results as dict of {axis: score, ...}
    scores = Questions.get_scores(test=False)

    r_scores = {}
    for q_id, q_scores in scores.items():
        r_scores[q_id] = { axis: q_score*answers[q_id] for axis, q_score in q_scores.items() }
    r_sums = { axis: sum([ v[axis] for v in r_scores.values() ]) for axis in r_scores[1].keys() }
    max_scores = Questions.get_max_scores()
    return { axis: round(val/max_scores[axis], 2) for axis, val in r_sums.items() }


def validate_filtersets(filtersets):
    if filtersets["order"] not in ["random", "recent"]:
        return "Invalid sampling order."
    if not 0 < int(filtersets["limit"]) < 10000:
        return "Sample size must be between 0 and 10,000."
    
    return False


@v.route("/api/to_results", methods=["POST"])
def to_results():
    data = request.get_json()
    captcha_response = data["recaptcha"]
    secret_url = f"{current_app.config['RECAPTCHA_VERIFY_URL']}?secret={current_app.config['RECAPTCHA_SECRET_KEY']}&response={captcha_response}"
    verify_response = requests.post(url=secret_url).json()
    if not verify_response["success"]:
        return {"status": "Captcha Verification Failed"}, 401

    # Count answers for each question to add user data to pie
    get_answer_counts()

    # Add user's result to database
    test = True
    if test:
        session["results_id"] = "1006"
    else:
        results, valid = validate_results(
            demographics = data["demographics"],
            scores = session["results"],
            answers = session["answers"])
        if valid != True:
            return {"status": f"Result Validation Failed: {valid}. Contact developer to report issue."}, 401
        session["results_id"] = Results.add_result(results, return_id=True)

    # Return success, ajax will redirect to results, set new path for link to instructions
    session["template"] = "instructions"
    return {"status": "success", "results_id": session["results_id"]}, 200


@v.route("/api/to_form", methods=["POST"])
def to_form():
    data = request.get_json()
    answers = { int(q): int(answer) for q, answer in data["answers"].items() }
    results = calculate_results(answers)
    session["answers"] = answers
    session["results"] = results
    session["template"] = "form"
    return {"status": "success"}, 200


@v.route("/api/to_test", methods=["POST"])
def to_test():
    data = request.get_json()
    if data["action"] == "to_test":
        session["template"] = "test"
    return {"status": "success"}, 200


@v.route("/api/to_instructions", methods=["POST"])
def to_instructions():
    # Restart test button pressed
    data = request.get_json()
    if data["action"] == "to_instructions":
        session["template"] = "instructions"
    return {"status": "success"}, 200


@v.route("/api/data", methods=["POST"])
def data_api():
    if request.method == "POST":
        data = request.get_json()
        if data["action"] == "apply_filters":
            filter_data = data["data"]
            is_valid = validate_filtersets(filter_data)
            if is_valid != False:
                return json.dumps({"status": f"Filterset validation failed: {is_valid} Contact the developer if you think this is a mistake."}), 401 

            datasets = Results.get_filtered_datasets(filter_data)
            if "answer_counts" in session:
                datasets.insert(0, {
                    "name": "your_results",
                    "color": "salmon",
                    "count": 1,
                    "point_props": [1, 8],
                    "all_scores": [session["results"]],
                    "answer_counts": session["answer_counts"]
                })
            return json.dumps({"status": "success", "compass_datasets": datasets}), 200

        elif data["action"] == "get_all_results":
            all_results = Results.get_all_dct()
            return json.dumps({"status": "success", "all_results": all_results}), 200

        elif data["action"] == "get_legacy_results":
            with open(os.path.join(current_app.config['REL_DIR'], "application/data/legacy-data/record.csv"), "r", encoding="utf-8") as f:
                return json.dumps({"status": "success", "legacy_results": f.read()}), 200
        else:
            return json.dumps({"status": f"Error: Unknown action. Contact the developer if you think this is a mistake."}), 401 
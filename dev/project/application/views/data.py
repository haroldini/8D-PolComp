from flask import Blueprint, render_template, request, session, current_app, send_from_directory
from datetime import datetime
import json
import os

from application.controllers.questions import QuestionsController as Questions
from application.controllers.results import ResultsController as Results


v = Blueprint('data', __name__)

def add_user_data(datasets):
    if "answer_counts" in session:
        datasets.insert(0, {
            "name": "your_results",
            "color": "salmon",
            "count": 1,
            "point_props": [1, 8],
            "all_scores": [session["results"]],
            "answer_counts": session["answer_counts"]
        })

def validate_filtersets(filtersets):
    if filtersets["order"] not in ["random", "recent"]:
        return "Invalid sampling order."
    if not 0 < int(filtersets["limit"]) < 10000:
        return "Sample size must be between 0 and 10,000."
    
    return False

@v.route("/data", methods=["POST", "GET"])
def data():

    if request.method == "POST":
        data = request.get_json()
        if data["action"] == "apply_filters":
            filter_data = data["data"]
            is_valid = validate_filtersets(filter_data)
            if is_valid != False:
                return {"status": f"Filterset validation failed: {is_valid} Contact the developer if you think this is a mistake."}, 401 
            print(data)

            datasets = Results.get_filtered_datasets(filter_data)
            add_user_data(datasets)
            return json.dumps({"status": "success", "compass_datasets": datasets}), 200

        elif data["action"] == "get_all_results":
            all_results = Results.get_all_dct()
            return json.dumps({"status": "success", "all_results": all_results}), 200

        elif data["action"] == "get_legacy_results":
            with open(os.path.join(current_app.config['REL_DIR'], "application/data/legacy-data/record.csv"), "r", encoding="utf-8") as f:
                return json.dumps({"status": "success", "legacy_results": f.read()}), 200
        else:
            return {"status": f"Error: Unknown action. Contact the developer if you think this is a mistake."}, 401 


    # Default data to display
    questions = Questions.get_all()
    datasets = Results.get_filtered_datasets(filter_data={
        'order': 'random', 
        'limit': '1000', 
        'min-date': '2023-01-01',
        'max-date': datetime.now().isoformat(),
        'filtersets': [{
            'min-age': None, 
            'max-age': None, 
            'any-all': 'any', 
            'color': '#0db52e', 
            'country': [], 
            'religion': [], 
            'ethnicity': [], 
            'education': [], 
            'party': [], 
            'identities': []
            }]
    })
    
    add_user_data(datasets)

    data = {
        "questions": questions,
        "columns": questions[0].__mapper__.column_attrs.keys(),
        "compass_datasets": json.dumps(datasets),
        "completed_count": Results.get_count()
    }
    with open(os.path.join(current_app.config['REL_DIR'], "application/data/demographics/demographics.json"), "r", encoding="utf-8") as f:
        demo = json.load(f)
        f.close()
    return render_template("pages/data.html", data=data, demo=demo)
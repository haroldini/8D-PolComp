from flask import Blueprint, render_template, request, session, current_app, send_from_directory
from datetime import datetime
import json
import os

from application.controllers.questions import QuestionsController as Questions
from application.controllers.results import ResultsController as Results


v = Blueprint('data', __name__)


@v.route("/data", methods=["GET"])
def data():

    # Default data to display
    questions = Questions.get_all()
    datasets = Results.get_filtered_datasets(filter_data={
        'order': 'random', 
        'limit': '1000', 
        'min-date': '2023-01-01',
        'max-date': datetime.now().isoformat(),
        'filtersets': [{
            'label': 'Filterset 1',
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
    
    if "answer_counts" in session:
        datasets.insert(0, {
            "name": "your_results",
            "label": "Your Results",
            "custom_dataset": False,
            "result_id": session["results_id"],
            "color": "salmon",
            "count": 1,
            "point_props": [1, 8],
            "all_scores": [session["results"]],
            "answer_counts": session["answer_counts"]
        })

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
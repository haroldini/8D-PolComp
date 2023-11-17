from flask import Blueprint, render_template
import json

from application.controllers.results import ResultsController as Results


v = Blueprint('index', __name__)


@v.route("/", methods=["GET"])
def index():  

    # Retrieve most recent submission from Results, pass as jinja variable into meta tag.
    data = {
        "compass_datasets": json.dumps([{
            "name": "sample_data",
            "label": f"Most Recent Result",
            "custom_dataset": False,
            "result_id": None,
            "count": 1,
            "color": "rgb(38, 38, 38)",
            "all_scores": [result.scores for result in Results.get_recent_results()]
        }]),
        "completed_count": Results.get_count()
    }
    return render_template("pages/index.html", data=data)





import json
import logging
import os
from datetime import date

from flask import Blueprint, render_template, session, current_app

from application.controllers.questions import QuestionsController as Questions
from application.controllers.results import ResultsController as Results


logger = logging.getLogger(__name__)


v = Blueprint("data", __name__)


@v.route("/data", methods=["GET"])
def data():
    """
    Render the data exploration page.

    Args:
        None

    Returns:
        Response: HTML data page template.

    Raises:
        500: Logs unexpected failures and serves minimal/empty state.
    """

    try:
        # Default data to display
        questions = Questions.get_all()

        datasets = []

        if "answer_counts" in session:
            datasets.insert(0, {
                "name": "your_results",
                "label": "Your Results",
                "custom_dataset": False,
                "result_id": session.get("results_id"),
                "color": "salmon",
                "count": 1,
                "point_props": [1, 8],
                "all_scores": [session.get("results")],
                "answer_counts": session.get("answer_counts")
            })

        columns = []
        if questions:
            columns = list(questions[0].__mapper__.column_attrs.keys())

        data = {
            "questions": questions,
            "columns": columns,
            "compass_datasets": json.dumps(datasets),
            "completed_count": Results.get_count()
        }

        demo_path = os.path.join(current_app.config["REL_DIR"], "application/data/demographics/demographics.json")
        with open(demo_path, "r", encoding="utf-8") as f:
            demo = json.load(f)

        return render_template("pages/data.html", data=data, demo=demo)

    except Exception:
        logger.exception("[/data] Failed to render data page")
        data = {
            "questions": [],
            "columns": [],
            "compass_datasets": json.dumps([]),
            "completed_count": 0
        }
        return render_template("pages/data.html", data=data, demo={})

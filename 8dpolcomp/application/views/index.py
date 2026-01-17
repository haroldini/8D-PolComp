
import json
import logging

from flask import Blueprint, render_template

from application.controllers.results import ResultsController as Results


logger = logging.getLogger(__name__)


v = Blueprint("index", __name__)


@v.route("/", methods=["GET"])
def index():
    """
    Render the homepage.

    Args:
        None

    Returns:
        Response: HTML homepage template.

    Raises:
        500: Logs unexpected failures and serves a minimal page state.
    """

    # Retrieve most recent submission from Results, pass as jinja variable into meta tag.
    try:
        recent_results = Results.get_recent_results()
        data = {
            "compass_datasets": json.dumps([{
                "name": "sample_data",
                "label": "Most Recent Result",
                "custom_dataset": False,
                "result_id": None,
                "count": 1,
                "color": "rgb(38, 38, 38)",
                "all_scores": [result.scores for result in recent_results]
            }]),
            "completed_count": Results.get_count(),
            "recent_results_id": recent_results[0].id if recent_results else None
        }
    except Exception:
        logger.exception("[/] Failed to load homepage data")
        data = {
            "compass_datasets": json.dumps([]),
            "completed_count": 0,
            "recent_results_id": None
        }

    return render_template("pages/index.html", data=data)

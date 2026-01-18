
import json
import logging

from flask import Blueprint, render_template

from application.controllers.results import ResultsController as Results


logger = logging.getLogger(__name__)


v = Blueprint("index", __name__)


def _zero_axes() -> dict:
    return {
        "diplomacy": 0,
        "economics": 0,
        "government": 0,
        "politics": 0,
        "religion": 0,
        "society": 0,
        "state": 0,
        "technology": 0
    }


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

    try:
        data = {
            "compass_datasets": json.dumps([
                {
                    "name": "index_recent1000_cloud",
                    "label": "1000 Recent",
                    "custom_dataset": False,
                    "result_id": None,
                    "count": 1000,
                    "color": "#0d56b5",
                    "all_scores": []
                },
                {
                    "name": "index_marker",
                    "label": "Marker",
                    "custom_dataset": False,
                    "result_id": None,
                    "count": 1,
                    "color": "rgb(38, 38, 38)",
                    "all_scores": [_zero_axes()]
                }
            ]),
            "completed_count": Results.get_count()
        }
    except Exception:
        logger.exception("[/] Failed to load homepage data")
        data = {
            "compass_datasets": json.dumps([]),
            "completed_count": 0
        }

    return render_template("pages/index.html", data=data)

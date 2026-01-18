
import json
import logging
import os

import numpy as np

from flask import Blueprint, render_template, current_app, session, redirect, url_for

from application.controllers.results import ResultsController as Results


logger = logging.getLogger(__name__)


v = Blueprint("results", __name__)


def euclidean_distances(results, avgs, power=1.3):
    if not isinstance(results, dict) or not isinstance(avgs, dict):
        raise ValueError("Invalid distance inputs")

    distances = {}
    for identity, avg in avgs.items():
        keys = set(results.keys()).union(avg.keys())
        distance = 1 / (1 + np.linalg.norm([abs(results.get(key, 0) - avg.get(key, 0)) ** power for key in keys]))
        distances[identity] = distance
    return sorted(distances.items(), key=lambda x: x[1], reverse=True)


def get_closest_matches(results):
    try:
        avg_path = os.path.join(current_app.config["REL_DIR"], "application/data/demographics/axis_averages.json")
        with open(avg_path, "r", encoding="utf-8") as f:
            avgs = json.load(f)
    except Exception:
        logger.exception("[get_closest_matches] Failed to load axis_averages.json")
        return {"overall": []}

    axes = results.keys()
    distances_by_axis = {"overall": euclidean_distances(results, avgs, power=1)}

    for axis in axes:
        single_axis_result = {axis: results[axis]}
        distances_by_axis[axis] = euclidean_distances(single_axis_result, avgs, power=1.5)

    return distances_by_axis


def serve_results_by_id(results_id, result_name, color):
    """
    Render results for a specific result ID.

    Args:
        results_id (int): Database result ID.
        result_name (str): Display name for the result.
        color (str): Plot colour for the dataset.

    Returns:
        Response: HTML results template.

    Raises:
        302: Redirects to instructions if results cannot be loaded.
    """
    try:
        id_results = Results.get_results_from_id(results_id + 1)
    except Exception:
        logger.exception("[serve_results_by_id] DB query failed: results_id=%s", results_id)
        session["template"] = "instructions"
        return redirect(url_for("instructions.instructions"))

    if id_results is None:
        session["template"] = "instructions"
        return redirect(url_for(f"{session['template']}.{session['template']}"))

    try:
        scores = id_results.scores
        group_id = str(id_results.group_id) if getattr(id_results, "group_id", None) else None

        data = {
            "compass_datasets": json.dumps([{
                "name": f"test_no_{result_name.replace(' ', '_')}",
                "label": f"Test #{result_name}",
                "custom_dataset": False,
                "result_id": results_id,
                "color": color,
                "count": 1,
                "point_props": [1, 8],
                "all_scores": [scores],
            }]),
            "results_id": results_id,
            "closest_matches": json.dumps(get_closest_matches(scores)),
            "group_id": group_id
        }
    except Exception:
        logger.exception("[serve_results_by_id] Failed to build result response: results_id=%s", results_id)
        session["template"] = "instructions"
        return redirect(url_for("instructions.instructions"))

    return render_template("pages/results.html", data=data)


@v.route("/results/<int:results_id>", methods=["GET"])
def results(results_id=None):
    """
    Render a results page by result ID.

    Args:
        results_id (int): Result ID from the URL.

    Returns:
        Response: HTML results template.

    Raises:
        302: Redirects to instructions if results_id is missing/invalid.
    """
    if results_id is not None:
        return serve_results_by_id(results_id, f"Test #{results_id}", "salmon")

    session["template"] = "instructions"
    return redirect(url_for("instructions.instructions"))

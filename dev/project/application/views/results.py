from flask import Blueprint, render_template, current_app, session, request, redirect, url_for
import numpy as np
import json
import os

from application.controllers.results import ResultsController as Results


v = Blueprint('results', __name__)


def euclidean_distances(results, avgs):
    """Calculate the Euclidean distance between two dictionaries of axes"""
    distances = {}
    max_dist = np.sqrt(len(results.keys())*2)
    for identity, avg in avgs.items():
        keys = set(results.keys()).union(avg.keys())
        distance = 1 / (1 + np.linalg.norm([results.get(key, 0) - avg.get(key, 0) for key in keys]))
        distances[identity] = distance
    return sorted(distances.items(), key=lambda x: x[1], reverse=True)


def get_closest_matches(results):
    """Determine the closest matches overall & for each axis"""
    with open(os.path.join(current_app.config['REL_DIR'], "application/data/demographics/axis_averages.json"), "r", encoding="utf-8") as f:
        avgs = json.load(f)

    # Get closest matches overall
    axes = results.keys()
    distances_by_axis = {"overall": euclidean_distances(results, avgs)}

    # Get closest matches for each axis
    for axis in axes:
        n_ax = len(axes)
        distances = [(identity, (1-2*abs(results[axis] - identity_avgs[axis]))/1) for identity, identity_avgs in avgs.items()]
        distances_by_axis[axis] = sorted(distances, key=lambda x: x[1], reverse=True)
        
    return distances_by_axis


def serve_results_by_id(results_id, result_name, color):
    # Get custom id results. if doesn't exist, return instructions
    id_results = Results.get_results_from_id(results_id+1)
    if id_results is None:
        session["template"] = "instructions"
        return redirect(url_for(f"{session['template']}.{session['template']}"))
    
    # Process custom results
    scores = id_results.scores
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
        "closest_matches": json.dumps(get_closest_matches(scores))
    }
    return render_template(f"pages/results.html", data=data)


@v.route("/results/<int:results_id>", methods=["GET"])
def results(results_id=None):

    # Serve specific result if given
    if results_id is not None:
        return serve_results_by_id(results_id, f"Test #{results_id}", "salmon")
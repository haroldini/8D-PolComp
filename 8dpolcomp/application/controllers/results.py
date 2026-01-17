
import logging
from datetime import datetime

import numpy as np
from sklearn.preprocessing import MaxAbsScaler
from sqlalchemy import or_, and_
from sqlalchemy.sql.expression import func
from sqlalchemy_filtering.filter_util import filter_apply
from sqlalchemy_filtering.operators import SQLDialect
from sqlalchemy_filtering.validators import FilterRequest

from application.models.results import Results
from application import db


logger = logging.getLogger(__name__)


class ResultsController:
    """
    Results CRUD + dataset filtering logic.

    These methods assume an active Flask app context.
    """

    def get_all():
        """
        Fetch all results.

        Returns:
            list[Results]
        """
        return Results.query.all()


    def get_all_dct():
        """
        Fetch all results as JSON-serialisable dicts.

        Returns:
            list[dict]
        """
        all_results = ResultsController.get_all()
        return [{
            "date": str(result.date),
            "results": result.scores,
            "answers": result.answers,
            "demographics": result.demographics,
        } for result in all_results]


    def get_all_scores():
        """
        Fetch only score blobs.

        Returns:
            list[dict]
        """
        return [result.scores for result in ResultsController.get_all()]


    def get_count():
        """
        Count all stored results.

        Returns:
            int
        """
        return Results.query.count()


    def get_recent_results(n=1):
        """
        Fetch the most recent results.

        Args:
            n (int): number of results

        Returns:
            list[Results]
        """
        return Results.query.order_by(Results.id.desc()).limit(n).all()


    def get_random_results(n=1):
        """
        Fetch random results.

        Args:
            n (int): number of results

        Returns:
            list[Results]
        """
        return Results.query.order_by(func.random()).limit(n).all()


    def get_results_from_id(id):
        """
        Fetch a single result by DB ID.

        Args:
            id (int)

        Returns:
            Results | None
        """
        return Results.query.filter_by(id=id).first()


    def add_result(results, return_id=False):
        """
        Insert a new result row.

        Args:
            results (dict): {"demographics": ..., "scores": ..., "answers": ...}
            return_id (bool): if True, return inserted id

        Returns:
            int | None
        """
        try:
            new_result = Results(**results)
            db.session.add(new_result)
            db.session.flush()
            db.session.commit()
            if return_id:
                return new_result.id
        except Exception:
            logger.exception("[ResultsController.add_result] DB insert failed")
            db.session.rollback()
            raise


    # Filter a provided query object using the filterset given
    def get_filtered_dataset(query, filterset, limit=None):
        """
        Apply one filterset to a SQLAlchemy query and return matching rows.

        Args:
            query: SQLAlchemy query
            filterset (dict): frontend filterset
            limit (int | str | None): max rows

        Returns:
            list[Results]
        """
        obj = {"filter": []}

        # Filtration for identities using sqlalchemy
        if len(filterset["identities"]) > 0:
            if filterset["any-all"] == "any":
                identity_filters = [
                    Results.demographics["identities"].comparator.contains([identity])
                    for identity in filterset["identities"]
                ]
                query_filt = query.filter(or_(*identity_filters))
            else:
                query_filt = query.filter(
                    Results.demographics["identities"].comparator.contains(filterset["identities"])
                )
        else:
            query_filt = query

        # Filtration for age using sqlalchemy-filtering
        if filterset["min-age"] is not None or filterset["max-age"] is not None:
            min_age = 0
            max_age = 101
            if filterset["min-age"] is not None and filterset["min-age"] > 0:
                min_age = filterset["min-age"]
            if filterset["max-age"] is not None and filterset["max-age"] > 0:
                max_age = filterset["max-age"]

            obj["filter"].append({
                "field": "demographics",
                "node": "age",
                "operator": ">=",
                "value": min_age,
            })

            obj["filter"].append({
                "field": "demographics",
                "node": "age",
                "operator": "<=",
                "value": max_age,
            })

        # Filtration for individual selections using sqlalchemy-filtering
        filter_keys = ["country", "religion", "ethnicity", "education", "party"]
        for filter_key in filter_keys:
            if len(filterset[filter_key]) > 0:
                obj["filter"].append({
                    "field": "demographics",
                    "node": filter_key,
                    "operator": "in",
                    "value": filterset[filter_key],
                })

        try:
            res = filter_apply(query=query_filt, entity=Results, obj=FilterRequest(obj), dialect=SQLDialect.POSTGRESQL)
        except Exception:
            logger.exception("[ResultsController.get_filtered_dataset] filter_apply failed")
            raise

        try:
            if limit is not None:
                res = res.limit(int(limit))
            return res.all()
        except Exception:
            logger.exception("[ResultsController.get_filtered_dataset] query execution failed")
            raise


    def get_filtered_datasets(filter_data):
        """
        Build datasets for the frontend data explorer.

        Args:
            filter_data (dict)

        Returns:
            list[dict]
        """
        datasets = []

        # Sort query and limit by date before filtering.
        if filter_data["order"] == "recent":
            query = Results.query.order_by(Results.id.desc())
        elif filter_data["order"] == "random":
            query = Results.query.order_by(func.random())
        else:
            query = Results.query.order_by(func.random())

        query = query.filter(and_(Results.date >= filter_data["min-date"], Results.date <= filter_data["max-date"]))

        for i, filterset in enumerate(filter_data["filtersets"]):
            filt_results = ResultsController.get_filtered_dataset(query, filterset, filter_data["limit"])
            all_scores = [result.scores for result in filt_results]
            all_answers = [result.answers for result in filt_results]

            raw_answer_counts = {
                str(q_id): {"Strongly Agree": 0, "Agree": 0, "Neutral": 0, "Disagree": 0, "Strongly Disagree": 0}
                for q_id in range(1, 101)
            }
            keys = {2: "Strongly Agree", 1: "Agree", 0: "Neutral", -1: "Disagree", -2: "Strongly Disagree"}

            for answer in all_answers:
                for q_id, q_ans in answer.items():
                    raw_answer_counts[str(q_id)][keys[q_ans]] += 1

            answer_counts = {}
            scaler = MaxAbsScaler()
            for q_id, inner_dict in raw_answer_counts.items():
                scaled_values = scaler.fit_transform([[value] for value in inner_dict.values()])
                scaled_dict = {category: scaled_values[i][0] for i, category in enumerate(inner_dict.keys())}
                answer_counts[q_id] = scaled_dict

            if len(all_scores) > 0:
                mean_scores = {key: round(np.mean([scores[key] for scores in all_scores]), 2) for key in all_scores[0].keys()}
                median_scores = {key: round(np.median([scores[key] for scores in all_scores]), 2) for key in all_scores[0].keys()}
            else:
                mean_scores = {}
                median_scores = {}

            datasets.append({
                "name": f"custom_{i}",
                "label": filterset["label"],
                "custom_dataset": True,
                "custom_id": i,
                "result_id": None,
                "color": filterset["color"],
                "count": len(all_scores),
                "raw_answer_counts": raw_answer_counts,
                "answer_counts": answer_counts,
                "all_scores": all_scores,
                "mean_scores": mean_scores,
                "median_scores": median_scores
            })

        return datasets


    def get_filtered_dataset_count(filter_data):
        """
        Return only counts for each filterset.

        Args:
            filter_data (dict)

        Returns:
            dict[int,int]
        """
        datasets = ResultsController.get_filtered_datasets(filter_data)
        counts = {dataset["custom_id"]: dataset["count"] for dataset in datasets}
        return counts


    def get_avg_identities(identity_keys, min_results=50):
        """
        Compute mean axis scores per identity.

        Args:
            identity_keys (list[str])
            min_results (int)

        Returns:
            dict[str, dict]
        """
        avg_identities = {}

        for identity_key in identity_keys:
            datasets = ResultsController.get_filtered_datasets(filter_data={
                "order": "random",
                "limit": "1000000",
                "min-date": "2023-01-01",
                "max-date": datetime.now().isoformat(),
                "filtersets": [{
                    "label": "All",
                    "min-age": None,
                    "max-age": None,
                    "any-all": "any",
                    "color": "#0db52e",
                    "country": [],
                    "religion": [],
                    "ethnicity": [],
                    "education": [],
                    "party": [],
                    "identities": [identity_key] if identity_key != "Average Result" else []
                }]
            })

            num_identities = len(datasets[0]["all_scores"])
            if num_identities > min_results:
                avg_identities[identity_key] = datasets[0]["mean_scores"]

        return avg_identities

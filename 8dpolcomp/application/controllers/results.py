
import logging
from datetime import date, datetime

import numpy as np
from sqlalchemy import and_, cast, Integer, Float, or_
from sqlalchemy.sql.expression import func

from application.models.results import Results
from application import db


logger = logging.getLogger(__name__)


def _coerce_to_date_bounds(min_val, max_val) -> tuple[date, date]:
    """
    Convert incoming min/max values (date/datetime) into DATE bounds suitable for DB filtering.
    """

    if isinstance(min_val, datetime):
        min_d = min_val.date()
    elif isinstance(min_val, date):
        min_d = min_val
    else:
        raise TypeError("min-date must be a date or datetime")

    if isinstance(max_val, datetime):
        max_d = max_val.date()
    elif isinstance(max_val, date):
        max_d = max_val
    else:
        raise TypeError("max-date must be a date or datetime")

    return min_d, max_d


class ResultsController:
    """
    Results CRUD + dataset filtering logic.
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
            "date": result.date.isoformat() if getattr(result, "date", None) else None,
            "group_id": str(result.group_id) if getattr(result, "group_id", None) else None,
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


    def _apply_filterset(query, filterset):
        """
        Apply filterset constraints directly in SQLAlchemy, matching JSON expression indexes.

        Args:
            query: SQLAlchemy query
            filterset (dict): frontend filterset

        Returns:
            SQLAlchemy query
        """

        # Group tests: group_id IN (...)
        group_ids = filterset.get("group-ids") or []
        if len(group_ids) > 0:
            query = query.filter(Results.group_id.in_(group_ids))

        # Identities: JSONB array containment
        identities = filterset.get("identities") or []
        if len(identities) > 0:
            if filterset.get("any-all") == "any":
                identity_filters = [
                    Results.demographics["identities"].comparator.contains([identity])
                    for identity in identities
                ]
                query = query.filter(or_(*identity_filters))
            else:
                query = query.filter(
                    Results.demographics["identities"].comparator.contains(identities)
                )

        # Age: cast to int for numeric comparisons + expression index usage
        min_age = filterset.get("min-age")
        max_age = filterset.get("max-age")

        if min_age is not None or max_age is not None:
            lo = int(min_age) if (min_age is not None and int(min_age) > 0) else 0
            hi = int(max_age) if (max_age is not None and int(max_age) > 0) else 101

            age_expr = cast(Results.demographics["age"].astext, Integer)
            query = query.filter(and_(age_expr >= lo, age_expr <= hi))

        # Scalar demographic fields: extraction for expression index usage
        filter_keys = ["country", "religion", "ethnicity", "education", "party"]
        for filter_key in filter_keys:
            vals = filterset.get(filter_key) or []
            if len(vals) > 0:
                query = query.filter(Results.demographics[filter_key].astext.in_(vals))

        return query


    # Filter a provided query object using the filterset given
    def get_filtered_dataset(query, filterset, limit=None):
        """
        Apply one filterset to a SQLAlchemy query and return matching rows.

        Args:
            query: SQLAlchemy query
            filterset (dict): frontend filterset
            limit (int | None): max rows

        Returns:
            list[Results]
        """

        query_filt = ResultsController._apply_filterset(query, filterset)

        if limit is not None:
            query_filt = query_filt.limit(int(limit))

        return query_filt.all()


    def get_filtered_dataset_query(query, filterset):
        """
        Apply one filterset to a SQLAlchemy query and return the query object.

        Args:
            query: SQLAlchemy query
            filterset (dict): frontend filterset

        Returns:
            SQLAlchemy query
        """
        return ResultsController._apply_filterset(query, filterset)


    # Returns list of dataset dictionaries containing scores, average scores and answers.
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

        min_d, max_d = _coerce_to_date_bounds(filter_data["min-date"], filter_data["max-date"])
        query = query.filter(and_(Results.date >= min_d, Results.date <= max_d))

        limit = filter_data.get("limit")
        limit = int(limit) if limit is not None else None

        # Reuse same query for each filterset
        for i, filterset in enumerate(filter_data["filtersets"]):
            filt_query = ResultsController.get_filtered_dataset_query(query, filterset)

            if limit is not None:
                filt_query = filt_query.limit(limit)

            # Only pull the JSON needed by the charts
            rows = filt_query.with_entities(Results.scores, Results.answers).all()

            all_scores = []
            raw_answer_counts = {
                str(q_id): {"Strongly Agree": 0, "Agree": 0, "Neutral": 0, "Disagree": 0, "Strongly Disagree": 0}
                for q_id in range(1, 101)
            }
            keys = {2: "Strongly Agree", 1: "Agree", 0: "Neutral", -1: "Disagree", -2: "Strongly Disagree"}

            for scores, answers in rows:
                all_scores.append(scores)
                for q_id, q_ans in answers.items():
                    raw_answer_counts[str(q_id)][keys[q_ans]] += 1

            # Get scaled answer counts (per-question max -> 1)
            answer_counts = {}
            for q_id, inner_dict in raw_answer_counts.items():
                denom = max(inner_dict.values()) or 1
                answer_counts[q_id] = {k: (v / denom) for k, v in inner_dict.items()}

            # Get mean and median scores for each axis
            if len(all_scores) > 0:
                axes = list(all_scores[0].keys())
                mat = np.array([[scores.get(axis, 0) for axis in axes] for scores in all_scores], dtype=float)

                mean_scores = {axis: round(float(np.mean(mat[:, j])), 2) for j, axis in enumerate(axes)}
                median_scores = {axis: round(float(np.median(mat[:, j])), 2) for j, axis in enumerate(axes)}
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

        min_d, max_d = _coerce_to_date_bounds(filter_data["min-date"], filter_data["max-date"])
        base_query = Results.query.filter(and_(Results.date >= min_d, Results.date <= max_d))

        limit = filter_data.get("limit")
        limit = int(limit) if limit is not None else None

        counts = {}

        for i, filterset in enumerate(filter_data["filtersets"]):
            q = ResultsController.get_filtered_dataset_query(base_query, filterset)

            q = q.order_by(None)

            n = q.with_entities(func.count(Results.id)).scalar() or 0

            if limit is not None:
                n = min(int(n), int(limit))

            counts[i] = int(n)

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

        axes = ["diplomacy", "economics", "government", "politics", "religion", "society", "state", "technology"]

        avg_identities = {}
        min_d = date(2023, 1, 1)
        max_d = date.today()

        for identity_key in identity_keys:
            avg_cols = [
                func.avg(cast(Results.scores[axis].astext, Float)).label(axis)
                for axis in axes
            ]

            q = db.session.query(
                func.count(Results.id).label("n"),
                *avg_cols
            ).filter(and_(Results.date >= min_d, Results.date <= max_d))

            if identity_key != "Average Result":
                q = q.filter(Results.demographics["identities"].comparator.contains([identity_key]))

            row = q.first()
            if not row:
                continue

            n = int(row.n or 0)
            if n > min_results:
                avg_identities[identity_key] = {
                    axis: round(float(getattr(row, axis) or 0.0), 2)
                    for axis in axes
                }

        return avg_identities

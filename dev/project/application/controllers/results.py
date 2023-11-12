from sqlalchemy.sql.expression import func
from sqlalchemy import or_, and_
from sqlalchemy_filtering.filter_util import filter_apply
from sqlalchemy_filtering.operators import SQLDialect
from sqlalchemy_filtering.validators import FilterRequest
from sklearn.preprocessing import MaxAbsScaler
from datetime import datetime
import numpy as np


from application.models.results import Results
from application import db

class ResultsController:
    def get_all():
        return Results.query.all()
    
    def get_all_dct():
        all_results = ResultsController.get_all()
        return [{
            "date": str(result.date),
            "results": result.scores,
            "answers": result.answers,
            "demographics": result.demographics,
            } for result in all_results ]
    
    def get_all_scores():
        return [result.scores for result in ResultsController.get_all()]

    def get_count():
        return Results.query.count()
    
    def get_recent_results(n=1):
        return Results.query.order_by(Results.id.desc()).limit(n).all()
    
    def get_random_results(n=1):
        return Results.query.order_by(func.random()).limit(n).all()

    def get_results_from_id(id):
        return Results.query.filter_by(id=id).first()

    def add_result(results, return_id):    
        new_result = Results(**results)
        db.session.add(new_result)
        db.session.flush()
        db.session.commit()
        if return_id:
            return new_result.id

    # Filter a provided query object using the filterset given
    def get_filtered_dataset(query, filterset, limit=None):
        obj = {"filter": []}

        # Filtration for identities using sqlalchemy
        if len(filterset["identities"]) > 0:
            if filterset["any-all"] == "any":
                query_filt = query.filter(or_(
                    Results.demographics["identities"].comparator.contains([identity])
                    for identity in filterset["identities"]
                    ))
            else:
                query_filt = query.filter(Results.demographics["identities"].comparator.contains(filterset["identities"]))
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
                obj["filter"].append(
                    {
                    "field": "demographics",
                    "node": filter_key,
                    "operator": "in",
                    "value": filterset[filter_key],
                    }
                )
        
        # Apply sqlalchemy-filtering filter to query
        res = filter_apply(query=query_filt, entity=Results, obj=FilterRequest(obj), dialect=SQLDialect.POSTGRESQL)
        
        if limit:
            results = res.limit(limit)
        return results.all()

    # Returns list of dataset dictionaries containing scores, average scores and answers.
    def get_filtered_datasets(filter_data):
        datasets = []

        # Sort query and limit by date before filtering.
        if filter_data["order"] == "recent":
            query = Results.query.order_by(Results.id.desc())
        elif filter_data["order"] == "random":
            query = Results.query.order_by(func.random())
        query = query.filter(
            and_(Results.date >= filter_data["min-date"], Results.date <= filter_data["max-date"])
        ) 

        # Reuse same query for each filterset
        for i, filterset in enumerate(filter_data["filtersets"]):
            filt_results = ResultsController.get_filtered_dataset(query, filterset, filter_data["limit"])
            all_scores = [result.scores for result in filt_results]
            all_answers = [result.answers for result in filt_results]

            # Get count of each answer for each question
            raw_answer_counts = {
                str(q_id): {"Strongly Agree": 0, "Agree": 0, "Neutral": 0, "Disagree": 0, "Strongly Disagree": 0} 
                for q_id in range(1, 101)}
            keys = {2: "Strongly Agree", 1: "Agree", 0: "Neutral", -1: "Disagree", -2: "Strongly Disagree"}
            for answer in all_answers:
                for q_id, q_ans in answer.items():
                    raw_answer_counts[q_id][keys[q_ans]] += 1

            # Get scaled answer counts
            answer_counts = {}
            scaler = MaxAbsScaler()
            for q_id, inner_dict in raw_answer_counts.items():
                scaled_values = scaler.fit_transform([[value] for value in inner_dict.values()])
                scaled_dict = {category: scaled_values[i][0] for i, category in enumerate(inner_dict.keys())}
                answer_counts[q_id] = scaled_dict

            # Get mean and median scores for each axis
            if len(all_scores) > 0:
                mean_scores = {key: round(np.mean([scores[key] for scores in all_scores]), 2) for key in all_scores[0].keys()}
                median_scores = {key: round(np.median([scores[key] for scores in all_scores]), 2) for key in all_scores[0].keys()}
            else:
                mean_scores = {}
                median_scores = {}

            datasets.append({
                "name": f"filterset_{i+1}",
                "color": filterset["color"],
                "count": len(all_scores),
                "raw_answer_counts": raw_answer_counts,
                "answer_counts": answer_counts,
                "all_scores": all_scores,
                "mean_scores": mean_scores,
                "median_scores": median_scores
            }) 

        return datasets
    
    # Returns a dictionary with identities as keys and average values for each axis
    def get_avg_identities(identity_keys, min_results=50):
        avg_identities = {}
        
        # datasets is a list of dictionaries.
        for identity_key in identity_keys:
            datasets = ResultsController.get_filtered_datasets(filter_data={
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
                    'identities': [identity_key]
                    }]
            })

            # only use if adquate scores in data
            num_identities = len(datasets[0]["all_scores"])
            if num_identities > min_results:
                avg_identities[identity_key] = datasets[0]["mean_scores"]
                
        return avg_identities
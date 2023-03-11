from sqlalchemy.sql.expression import func, select

from application.models.results import Results
from application import db

class ResultsController:
    def get_all():
        return Results.query.all()

    def get_count():
        return Results.query.count()
    
    def get_recent_results(n=1):
        return Results.query.order_by(Results.id.desc()).limit(n).all()
    
    def get_random_results(n=1):
        return Results.query.order_by(func.rand()).limit(n).all()

    def add_result(demographics, scores, answers):
        db.session.add(Results(
            demographics=demographics,
            scores=scores,
            answers=answers
            ))
        db.session.commit()
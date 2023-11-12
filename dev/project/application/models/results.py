from application import db
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB, DATE

class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(DATE, default=datetime.utcnow)
    demographics = db.Column(JSONB, nullable=False)
    scores = db.Column(JSONB, nullable=False)
    answers = db.Column(JSONB, nullable=False)

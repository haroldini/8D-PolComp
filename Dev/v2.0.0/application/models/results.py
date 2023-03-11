from application import db
from datetime import datetime

class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    demographics = db.Column(db.JSON, nullable=False)
    scores = db.Column(db.JSON, nullable=False)
    answers = db.Column(db.JSON, nullable=False)
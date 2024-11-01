from application import db

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    society = db.Column(db.Integer, nullable=False)
    politics = db.Column(db.Integer, nullable=False)
    economics = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    diplomacy = db.Column(db.Integer, nullable=False)
    government = db.Column(db.Integer, nullable=False)
    technology = db.Column(db.Integer, nullable=False)
    religion = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(255), nullable=False)

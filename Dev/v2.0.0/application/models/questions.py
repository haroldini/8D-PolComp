from sqlalchemy import Column, Numeric, String
from application import db

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dbq_question = db.Column(db.String, nullable=False)
    dbq_authlib = db.Column(db.Float, nullable=False)
    dbq_autodemo = db.Column(db.Float, nullable=False)
    dbq_nationglob = db.Column(db.Float, nullable=False)
    dbq_modrad = db.Column(db.Float, nullable=False)
    dbq_theosec = db.Column(db.Float, nullable=False)
    dbq_tradprog = db.Column(db.Float, nullable=False)
    dbq_primtrans = db.Column(db.Float, nullable=False)
    dbq_capsoc = db.Column(db.Float, nullable=False)

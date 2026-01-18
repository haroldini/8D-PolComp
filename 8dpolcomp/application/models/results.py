
from application import db
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB, DATE, UUID


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(DATE, default=lambda: datetime.now(timezone.utc).date())
    group_id = db.Column(UUID(as_uuid=True), nullable=True)
    demographics = db.Column(JSONB, nullable=False)
    scores = db.Column(JSONB, nullable=False)
    answers = db.Column(JSONB, nullable=False)
    how_found = db.Column(db.Text, nullable=True)

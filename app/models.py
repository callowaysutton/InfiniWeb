from app import db

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, unique=True, nullable=False)
    content = db.Column(db.String, nullable=False)
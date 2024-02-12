from app import db

class User(db.Model):
    iduser = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    password = db.Column(db.String(128))
    email = db.Column(db.String(30))
    is_delete = db.Column(db.Boolean, default=False)
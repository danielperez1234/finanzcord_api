from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    relevance = db.Column(db.String(255))
    meta = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), server_onupdate=db.func.current_timestamp())
    iduser = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_delete = db.Column(db.Integer)
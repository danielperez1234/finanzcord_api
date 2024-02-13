from app import db

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    concept = db.Column(db.String(255), nullable=False)
    idcategory = db.Column(db.Integer)
    amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), server_onupdate=db.func.current_timestamp())
    date = db.Column(db.Date)
    idpayment = db.Column(db.Integer)
    priority = db.Column(db.Integer)
    iduser = db.Column(db.Integer, db.ForeignKey('user.id'))
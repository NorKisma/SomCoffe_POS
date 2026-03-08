from app.extensions.db import db

class Table(db.Model):
    __tablename__ = 'tables'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, default=4)
    status = db.Column(db.String(20), default='available') # available, occupied, reserved
    
    orders = db.relationship('Order', backref='table', lazy=True)

    def __repr__(self):
        return f'<Table {self.number}>'

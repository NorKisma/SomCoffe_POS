from app.extensions.db import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='cash') # cash, card, mobile
    status = db.Column(db.String(20), default='completed')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    def __repr__(self):
        return f'<Payment {self.id}>'

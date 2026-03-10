from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=True)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending') # pending, completed, cancelled
    order_type = db.Column(db.String(20), default='dine-in') # dine-in, takeaway
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payment_status = db.Column(db.String(20), default='paid') # paid, unpaid, partial

    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='order', lazy=True)
    user = db.relationship('User', backref='orders', lazy=True)

    def __repr__(self):
        return f'<Order {self.id}>'

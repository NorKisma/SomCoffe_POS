from app.extensions import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    credit_limit = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='customer_rel', lazy=True)

    @property
    def current_debt(self):
        from app.models.order import Order
        unpaid_orders = Order.query.filter(
            Order.customer_id == self.id,
            Order.payment_status != 'paid'
        ).all()
        return sum(order.total_amount for order in unpaid_orders)

    def __repr__(self):
        return f'<Customer {self.name}>'

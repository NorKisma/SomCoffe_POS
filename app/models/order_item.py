from app.extensions import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_time = db.Column(db.Float, nullable=False)
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    # These relationships are also defined via backref in Order and Product, 
    # but defining them here improves IDE support.
    # order = db.relationship('Order', back_populates='items')
    # product = db.relationship('Product', back_populates='order_items')

    def __repr__(self):
        return f'<OrderItem {self.id}>'

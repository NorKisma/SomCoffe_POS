from app.models.order import Order
from app.extensions.db import db
from datetime import datetime

class OrderService:
    @staticmethod
    def get_paginated_orders(page, per_page):
        return Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_order_by_id(order_id):
        return Order.query.get_or_404(order_id)

    @staticmethod
    def get_order_details(order_id):
        order = Order.query.get_or_404(order_id)
        
        items = []
        for item in order.items:
            items.append({
                'product_name': item.product.name if item.product else 'Unknown',
                'quantity': item.quantity,
                'price': item.price_at_time,
                'total': item.quantity * item.price_at_time
            })
            
        return {
            'id': order.id,
            'table': order.table.number if order.table else 'Takeaway',
            'customer': order.customer_name or 'Guest',
            'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'type': order.order_type,
            'status': order.status,
            'total': order.total_amount,
            'items': items
        }

    @staticmethod
    def update_order(order_id, status, customer_name):
        order = Order.query.get_or_404(order_id)
        if status:
            order.status = status
        if customer_name is not None:
            order.customer_name = customer_name
            
        db.session.commit()
        return order

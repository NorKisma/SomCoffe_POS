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
                'product_name': item.product.name if item.product else 'Lama yaqaan',
                'quantity': item.quantity,
                'price': item.price_at_time,
                'total': item.quantity * item.price_at_time
            })
            
        user = order.user
        
        return {
            'id': order.id,
            'table': order.table.number if order.table else 'Takeaway',
            'customer': order.customer_rel.name if (hasattr(order, 'customer_rel') and order.customer_rel) else (order.customer_name or 'Macmiil'),
            'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'type': order.order_type,
            'status': order.status,
            'payment_status': order.payment_status or 'paid',
            'total': order.total_amount,
            'items': items,
            'served_by': user.username if user else 'Unknown',
            'evc_number': user.evc_number if user else None,
            'edahab_number': user.edahab_number if user else None
        }

    @staticmethod
    def update_order(order_id, status, customer_name):
        order = Order.query.get_or_404(order_id)
        
        # Restore stock and delete if order is being cancelled
        if status == 'cancelled':
            if order.status != 'cancelled':
                for item in order.items:
                    product = item.product
                    if product and getattr(product, 'stock', None) is not None and not getattr(product, 'is_service', False):
                        product.stock += item.quantity
                        
            # Delete associated payments if they exist
            if hasattr(order, 'payments'):
                for payment in order.payments:
                    db.session.delete(payment)
                    
            db.session.delete(order)
            db.session.commit()
            return None

        if status:
            order.status = status
        if customer_name is not None:
            order.customer_name = customer_name
            
        db.session.commit()
        return order

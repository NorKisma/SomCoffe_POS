from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.setting import Setting
from app.models.payment import Payment  # type: ignore
from app.extensions.db import db
from datetime import datetime

class POSService:
    @staticmethod
    def create_order(items, table_id, user_id, payment_method='Pending'):
        if not items:
            raise ValueError("Cart is empty")

        subtotal = sum(item['price'] * item['qty'] for item in items)
        vat_rate = float(Setting.get_val('vat_rate', '15')) / 100
        total_with_tax = subtotal * (1 + vat_rate)
        
        status = 'completed' if payment_method and payment_method != 'Pending' else 'pending'
        
        new_order = Order(
            table_id=table_id if table_id != 0 else None,
            total_amount=total_with_tax,
            status=status,
            order_type='dine-in' if table_id != 0 else 'takeaway',
            user_id=user_id
        )
        
        db.session.add(new_order)
        db.session.flush() # Get order ID
        
        for item in items:
            product = db.session.get(Product, item['id'])
            if not product:
                continue
                
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['id'],
                quantity=item['qty'],
                price_at_time=item['price']
            )
            db.session.add(order_item)
            
            # Update stock only for physical products
            if not getattr(product, 'is_service', False) and product.stock is not None:
                product.stock -= item['qty']
                
        # Record payment if a payment method is provided
        if payment_method and payment_method != 'Pending':
            new_payment = Payment(
                amount=total_with_tax,
                payment_method=payment_method,
                status='completed',
                order_id=new_order.id
            )
            db.session.add(new_payment)
                
        db.session.commit()
        return new_order

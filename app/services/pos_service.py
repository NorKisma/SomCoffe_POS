from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.setting import Setting
from app.models.payment import Payment  # type: ignore
from app.extensions.db import db
from datetime import datetime

class POSService:
    @staticmethod
    def get_active_order_for_table(table_id):
        return Order.query.filter_by(table_id=table_id, status='pending').first()

    @staticmethod
    def create_order(items, table_id, user_id, payment_method='Pending', customer_id=None, split_payment=None, order_id=None):
        if not items:
            raise ValueError("Cart is empty")

        # Check for existing order if order_id is provided
        existing_order = None
        if order_id:
            existing_order = db.session.get(Order, order_id)
        
        # If no order_id but it's a table order, check if we should append to an existing pending one
        if not existing_order and table_id and table_id != 0:
            existing_order = POSService.get_active_order_for_table(table_id)

        subtotal = sum(item['price'] * item['qty'] for item in items)
        vat_rate = float(Setting.get_val('vat_rate', '15')) / 100
        total_with_tax = subtotal * (1 + vat_rate)
        
        # Determine status and payment_status
        status = 'completed' if (payment_method and payment_method not in ['Pending']) else 'pending'
        
        if split_payment:
            paid_amt = split_payment.get('paid_amount', 0)
            credit_amt = split_payment.get('credit_amount', 0)
            if credit_amt > 0 and paid_amt > 0:
                payment_status = 'partial'
            elif credit_amt > 0:
                payment_status = 'unpaid'
            else:
                payment_status = 'paid'
            status = 'completed'
        else:
            is_credit = (payment_method == 'Credit')
            payment_status = 'unpaid' if (is_credit or payment_method == 'Pending') else 'paid'
            if payment_method == 'Pending': status = 'pending'

        if existing_order:
            # Update existing order total and status
            existing_order.total_amount += total_with_tax
            if status == 'completed':
                existing_order.status = 'completed'
                existing_order.payment_status = payment_status
            order = existing_order
        else:
            order = Order(
                table_id=table_id if table_id != 0 else None,
                customer_id=customer_id if customer_id != 0 else None,
                total_amount=total_with_tax,
                status=status,
                payment_status=payment_status,
                order_type='dine-in' if table_id != 0 else 'takeaway',
                user_id=user_id
            )
            db.session.add(order)
            db.session.flush() 
        
        for item in items:
            product = db.session.get(Product, item['id'])
            if not product: continue
                
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['id'],
                quantity=item['qty'],
                price_at_time=item['price']
            )
            db.session.add(order_item)
            
            if not getattr(product, 'is_service', False) and product.stock is not None:
                product.stock -= item['qty']
                
        # Handle Payments
        if split_payment:
            if split_payment.get('paid_amount', 0) > 0:
                db.session.add(Payment(
                    amount=split_payment['paid_amount'],
                    payment_method=split_payment['paid_method'],
                    status='completed',
                    order_id=order.id
                ))
            if split_payment.get('credit_amount', 0) > 0:
                db.session.add(Payment(
                    amount=split_payment['credit_amount'],
                    payment_method='Credit',
                    status='pending',
                    order_id=order.id
                ))
        elif payment_method and payment_method != 'Pending':
            db.session.add(Payment(
                amount=total_with_tax,
                payment_method=payment_method,
                status='completed' if payment_method != 'Credit' else 'pending',
                order_id=order.id
            ))
                
        db.session.commit()
        return order

from app.models.payment import Payment
from app.extensions.db import db

class PaymentService:
    @staticmethod
    def record_payment(order_id, amount, method, status='completed'):
        payment = Payment(
            order_id=order_id,
            amount=amount,
            payment_method=method,
            status=status
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def get_payments_by_order(order_id):
        return Payment.query.filter_by(order_id=order_id).all()

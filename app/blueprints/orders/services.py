from app.models.order import Order
from app.extensions.db import db

class OrdersModuleService:
    @staticmethod
    def get_order_by_id(order_id):
        return db.session.get(Order, order_id)

    @staticmethod
    def update_order_status(order_id, status):
        """Update order status and handle necessary database logic."""
        order = OrdersModuleService.get_order_by_id(order_id)
        if order:
            order.status = status
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_order(order_id):
        """Safely delete an order and associated records."""
        order = OrdersModuleService.get_order_by_id(order_id)
        if order:
            db.session.delete(order)
            db.session.commit()
            return True
        return False

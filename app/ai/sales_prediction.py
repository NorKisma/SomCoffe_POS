from app.extensions.db import db
from app.models.order import Order
from app.models.order_item import OrderItem
from datetime import datetime, timedelta
from sqlalchemy import func

class SalesPredictor:
    """
    Uses historical data to project future sales trends.
    """
    
    @staticmethod
    def predict_next_day_sales():
        """
        Simple moving average of the last 7 days.
        """
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        # Calculate daily averages
        total_sales = db.session.query(func.sum(Order.total_amount))\
            .filter(Order.created_at >= seven_days_ago, Order.status == 'completed')\
            .scalar() or 0.0
            
        projected_sales = total_sales / 7.0
        
        return {
            "prediction_type": "moving_average_7d",
            "projected_revenue": round(projected_sales, 2)
        }

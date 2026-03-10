from app.models.order import Order
from app.extensions.db import db
from sqlalchemy import func
from datetime import datetime, timedelta

class ReportsModuleService:
    @staticmethod
    def get_weekly_revenue():
        """Aggregates revenue for the past 7 days."""
        revenue_data = []
        for i in range(7):
            day = datetime.utcnow().date() - timedelta(days=i)
            total = db.session.query(func.sum(Order.total_amount)).filter(
                func.date(Order.created_at) == day,
                Order.status == 'completed'
            ).scalar() or 0.0
            revenue_data.append({'day': day.strftime('%a'), 'total': float(total)})
        return list(reversed(revenue_data))

    @staticmethod
    def get_revenue_by_status():
        """Break down revenue by order status."""
        return db.session.query(
            Order.status, 
            func.sum(Order.total_amount)
        ).group_by(Order.status).all()

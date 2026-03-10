from app.models.order import Order
from app.extensions.db import db
from sqlalchemy import func
from datetime import datetime, timedelta

class ReportService:
    @staticmethod
    def get_revenue_summary(days=7):
        start_date = datetime.utcnow() - timedelta(days=days)
        revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= start_date,
            Order.status == 'completed'
        ).scalar() or 0.0
        return float(revenue)

    @staticmethod
    def get_daily_revenue(days=7):
        start_date = datetime.utcnow() - timedelta(days=days)
        daily_sales = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('total')
        ).filter(
            Order.created_at >= start_date,
            Order.status == 'completed'
        ).group_by(func.date(Order.created_at)).all()
        
        return {str(d.date): float(d.total) for d in daily_sales}

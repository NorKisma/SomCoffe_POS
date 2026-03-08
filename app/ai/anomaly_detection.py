from app.models.order import Order
from app.extensions.db import db
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Scans past and current sales to flag highly unusual transactions.
    """
    
    @staticmethod
    def detect_high_amount_transactions(threshold=100.00):
        """
        Detect spikes where a single order amount is well beyond average.
        """
        unusual_orders = db.session.query(Order)\
            .filter(Order.total_amount > threshold)\
            .order_by(Order.created_at.desc())\
            .limit(10).all()
            
        anomalies = []
        for order in unusual_orders:
            anomalies.append({
                "order_id": order.id,
                "amount": order.total_amount,
                "time": order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "severity": "HIGH" if order.total_amount > threshold*2 else "MEDIUM"
            })
            
        if anomalies:
            logger.warning(f"[{datetime.now()}] Detected {len(anomalies)} potential anomalies!")
        return anomalies

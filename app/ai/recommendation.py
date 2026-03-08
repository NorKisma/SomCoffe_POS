from app.extensions.db import db
from app.models.product import Product
from app.models.order_item import OrderItem
from sqlalchemy import func

class Recommender:
    """
    Suggests popular items to be paired with other orders.
    """
    
    @staticmethod
    def get_top_performing_items(limit=3):
        """
        Returns the top configured number of selling items.
        """
        top_items = db.session.query(
            OrderItem.product_id, 
            func.sum(OrderItem.quantity).label('total_qty')
        )\
        .group_by(OrderItem.product_id)\
        .order_by(func.sum(OrderItem.quantity).desc())\
        .limit(limit)\
        .all()
        
        recommendations = []
        for p_id, total_qty in top_items:
            product = db.session.get(Product, p_id)
            if product:
                recommendations.append({
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "score": total_qty
                })
        return recommendations

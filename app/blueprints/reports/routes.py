from flask import render_template
from . import reports_bp
from app.models.order import Order
from app.models.product import Product
from app.extensions.db import db
import sqlalchemy

@reports_bp.route('/')
def index():
    # Calculate revenue
    total_revenue = db.session.query(sqlalchemy.func.sum(Order.total_amount)).scalar() or 0
    total_orders = Order.query.count()
    total_products = Product.query.count()
    
    # Revenue per status
    revenue_by_status = db.session.query(Order.status, sqlalchemy.func.sum(Order.total_amount)).group_by(Order.status).all()
    
    return render_template('reports/index.html', 
                          total_revenue=total_revenue,
                          total_orders=total_orders,
                          total_products=total_products,
                          revenue_by_status=revenue_by_status)

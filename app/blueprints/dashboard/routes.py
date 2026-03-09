from flask import render_template
from flask_login import login_required
from . import dashboard_bp
from app.models.order import Order
from app.models.employee import Employee
from app.models.product import Product
from app.models.category import Category
from app.extensions.db import db
from sqlalchemy import func
from datetime import datetime, timedelta

@dashboard_bp.route('/')
@login_required
def index():
    # 1. Real Stats
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
    total_orders = Order.query.count()
    total_employees = Employee.query.filter_by(status='active').count()
    
    # Peak Category (Most sold items)
    peak_cat = db.session.query(Category.name, func.count(Order.id))\
        .join(Product, Product.category_id == Category.id)\
        .join(Order, Order.id == Order.id)\
        .group_by(Category.name)\
        .order_by(func.count(Order.id).desc())\
        .first()
    
    peak_cat_name = peak_cat[0] if peak_cat else "N/A"

    # 2. Recent Orders Activity
    recent_activity = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    # 3. Inventory Alerts (Low Stock)
    low_stock_products = Product.query.filter(Product.stock <= 10, Product.is_service == False).limit(3).all()

    # 4. Chart Data (Last 7 Days)
    chart_days = []
    chart_revenue = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_str = day.strftime('%d %b')
        chart_days.append(day_str)
        
        rev = db.session.query(func.sum(Order.total_amount))\
            .filter(func.date(Order.created_at) == day.date())\
            .scalar() or 0
        chart_revenue.append(float(rev))

    return render_template('dashboard/dashboard.html',
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           total_employees=total_employees,
                           peak_cat_name=peak_cat_name,
                           recent_activity=recent_activity,
                           low_stock_products=low_stock_products,
                           chart_days=chart_days,
                           chart_revenue=chart_revenue)

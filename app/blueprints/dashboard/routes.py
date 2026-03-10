from flask import render_template
from flask_login import login_required, current_user
from . import dashboard_bp
from app.models.order import Order
from app.models.employee import Employee
from app.models.product import Product
from app.models.category import Category
from app.models.payment import Payment
from app.extensions.db import db
from sqlalchemy import func
from datetime import datetime, timedelta


def _today():
    """Today's date in local time."""
    return datetime.utcnow().date()


# ──────────────────────────────────────────────
#  WAITER STATS
# ──────────────────────────────────────────────
def _get_waiter_data():
    today = _today()
    orders_today = Order.query.filter(
        func.date(Order.created_at) == today,
        Order.user_id == current_user.id
    ).all()

    total_sales = sum(o.total_amount for o in orders_today)
    pending = [o for o in orders_today if o.status == 'pending']
    served = [o for o in orders_today if o.status == 'completed']

    # Recent 5 orders by this waiter
    recent = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc()).limit(5).all()

    return dict(
        orders_count=len(orders_today),
        total_sales=total_sales,
        pending_count=len(pending),
        served_count=len(served),
        recent_orders=recent,
    )


# ──────────────────────────────────────────────
#  CASHIER STATS
# ──────────────────────────────────────────────
def _get_cashier_data():
    today = _today()

    def _sum_method(method_name):
        # Sum payments for the given method today
        return db.session.query(func.sum(Payment.amount))\
            .join(Order)\
            .filter(
                func.date(Payment.timestamp) == today,
                Payment.payment_method == method_name
            ).scalar() or 0

    cash       = _sum_method('Cash')
    evc        = _sum_method('EVC Plus')
    edahab     = _sum_method('eDahab')
    credit     = _sum_method('Credit')
    total_today = cash + evc + edahab + credit

    # Orders waiting to be paid / closed
    open_orders = Order.query.filter(
        Order.status == 'pending',
        func.date(Order.created_at) == today
    ).all()

    # Last 5 payments
    recent_payments = Payment.query.join(Order)\
        .filter(func.date(Payment.timestamp) == today)\
        .order_by(Payment.timestamp.desc()).limit(5).all()

    return dict(
        cash=cash,
        evc=evc,
        edahab=edahab,
        credit=credit,
        total_today=total_today,
        open_orders=open_orders,
        recent_payments=recent_payments,
    )


# ──────────────────────────────────────────────
#  MANAGER / ADMIN STATS
# ──────────────────────────────────────────────
def _get_manager_data():
    today = _today()

    # Today totals
    total_today = db.session.query(func.sum(Order.total_amount))\
        .filter(func.date(Order.created_at) == today).scalar() or 0
    orders_today = Order.query.filter(
        func.date(Order.created_at) == today).count()
    pending_today = Order.query.filter(
        Order.status == 'pending',
        func.date(Order.created_at) == today).count()
    total_employees = Employee.query.filter_by(status='active').count()

    # Top product by qty sold
    from app.models.order_item import OrderItem
    top_product = db.session.query(
        Product.name, func.sum(OrderItem.quantity).label('qty')
    ).join(OrderItem, OrderItem.product_id == Product.id)\
     .join(Order, Order.id == OrderItem.order_id)\
     .filter(func.date(Order.created_at) == today)\
     .group_by(Product.name)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .first()

    peak_product = top_product[0] if top_product else 'N/A'

    # Chart – last 7 days revenue
    chart_days, chart_revenue = [], []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        chart_days.append(day.strftime('%d %b'))
        rev = db.session.query(func.sum(Order.total_amount))\
            .filter(func.date(Order.created_at) == day.date()).scalar() or 0
        chart_revenue.append(float(rev))

    # All-time totals for the main card row
    total_revenue_all = db.session.query(
        func.sum(Order.total_amount)).scalar() or 0
    total_orders_all = Order.query.count()

    # Recent 5 orders
    recent_activity = Order.query.order_by(
        Order.created_at.desc()).limit(5).all()

    # Low stock
    low_stock = Product.query.filter(
        Product.stock <= 10, Product.is_service == False).limit(3).all()

    return dict(
        total_today=total_today,
        orders_today=orders_today,
        pending_today=pending_today,
        total_employees=total_employees,
        peak_product=peak_product,
        chart_days=chart_days,
        chart_revenue=chart_revenue,
        total_revenue_all=total_revenue_all,
        total_orders_all=total_orders_all,
        recent_activity=recent_activity,
        low_stock_products=low_stock,
        # keep legacy keys
        total_revenue=total_revenue_all,
        total_orders=total_orders_all,
        peak_cat_name=peak_product,
    )


# ──────────────────────────────────────────────
#  MAIN ROUTE — dispatches by role
# ──────────────────────────────────────────────
@dashboard_bp.route('/')
@login_required
def index():
    role = current_user.role  # admin, manager, cashier, waiter

    if role in ('admin', 'manager'):
        data = _get_manager_data()
        return render_template('dashboard/manager.html', **data)

    elif role == 'cashier':
        data = _get_cashier_data()
        return render_template('dashboard/cashier.html', **data)

    else:  # waiter / staff
        data = _get_waiter_data()
        return render_template('dashboard/waiter.html', **data)

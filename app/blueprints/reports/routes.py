from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.utils.decorators import manager_required
from . import reports_bp
from app.models.order import Order
from app.models.product import Product
from app.models.employee import Employee
from app.models.expense import Expense
from app.models.user import User
from app.extensions.db import db
import sqlalchemy
from datetime import datetime, timedelta

@reports_bp.route('/')
@login_required
def index():
    # Date Filtering
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    today = datetime.now()
    
    # SECURITY: Only 'admin' or 'manager' sees everyone. 
    # Others ONLY see their own data.
    if current_user.role not in ('admin', 'manager'):
        user_id = current_user.id
    else:
        user_id = request.args.get('user_id', type=int)
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        # Default to today for a daily view
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        end_date = today

    # Prepare query filters for the date range
    end_date_filter = end_date + timedelta(days=1) - timedelta(microseconds=1)

    # Base Order Query for status breakdown
    all_orders = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date_filter
    )
    if user_id:
        all_orders = all_orders.filter(Order.user_id == user_id)
    
    # Calculate revenue (Orders that are paid or partially paid)
    # This is more accurate ('Xog Saxan') than just 'completed' status
    total_revenue_query = db.session.query(sqlalchemy.func.sum(Order.total_amount)).filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date_filter,
        Order.payment_status.in_(['paid', 'partial'])
    )
    if user_id:
        total_revenue_query = total_revenue_query.filter(Order.user_id == user_id)
        
    total_revenue = float(total_revenue_query.scalar() or 0.0)

    # Daily Revenue for Chart
    daily_revenue = []
    daily_labels = []
    curr = start_date
    while curr <= end_date:
        d_start = curr.replace(hour=0, minute=0, second=0)
        d_end = curr.replace(hour=23, minute=59, second=59)
        day_total = db.session.query(sqlalchemy.func.sum(Order.total_amount)).filter(
            Order.created_at >= d_start,
            Order.created_at <= d_end,
            Order.payment_status.in_(['paid', 'partial'])
        )
        if user_id:
            day_total = day_total.filter(Order.user_id == user_id)
        
        daily_revenue.append(float(day_total.scalar() or 0.0))
        daily_labels.append(curr.strftime('%b %d'))
        curr += timedelta(days=1)

    total_orders = all_orders.count()
    total_products = Product.query.count()
    
    # Revenue per status
    revenue_by_status = db.session.query(
        Order.status, sqlalchemy.func.sum(Order.total_amount)
    ).filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date_filter
    )
    if user_id:
        revenue_by_status = revenue_by_status.filter(Order.user_id == user_id)
    revenue_by_status = revenue_by_status.group_by(Order.status).all()
    
    # === PROFIT & LOSS CALCULATIONS ===
    # 1. Estimated COGS (Cost of goods sold) - 30% for restaurants if not tracked
    estimated_cogs = total_revenue * 0.30
    
    # 2. Gross Profit
    gross_profit = total_revenue - estimated_cogs
    
    # 3. Staff Salaries
    days_in_range = max((end_date.date() - start_date.date()).days + 1, 1)
    if user_id:
        # If user is selected, only show their apportioned salary if they are an employee
        emp = Employee.query.filter_by(user_id=user_id).first()
        total_monthly_salaries = emp.salary if emp else 0.0
    else:
        # Sum of all active employees
        total_monthly_salaries = db.session.query(sqlalchemy.func.sum(Employee.salary)).filter_by(status='active').scalar() or 0.0
    
    apportioned_salaries = (float(total_monthly_salaries) / 30.0) * days_in_range
    
    # 4. Other Expenses
    total_expenses = db.session.query(sqlalchemy.func.sum(Expense.amount)).filter(
        Expense.date >= start_date.date(),
        Expense.date <= end_date.date()
    ).scalar() or 0.0
    
    # 5. Net Profit
    net_profit = gross_profit - apportioned_salaries - float(total_expenses)

    # Fetch users for filter
    users = User.query.all()

    # 6. Dine-in vs Takeaway breakdown
    order_type_stats_query = db.session.query(
        Order.order_type, sqlalchemy.func.count(Order.id), sqlalchemy.func.sum(Order.total_amount)
    ).filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date_filter
    )
    if user_id:
        order_type_stats_query = order_type_stats_query.filter(Order.user_id == user_id)
        
    order_type_stats = order_type_stats_query.group_by(Order.order_type).all()

    # 7. Top Selling Products in this range
    from app.models.order_item import OrderItem
    top_selling_products_query = db.session.query(
        Product.name, sqlalchemy.func.sum(OrderItem.quantity).label('total_qty'), sqlalchemy.func.sum(OrderItem.quantity * OrderItem.price_at_time).label('total_rev')
    ).join(OrderItem, OrderItem.product_id == Product.id)\
     .join(Order, Order.id == OrderItem.order_id)\
     .filter(Order.created_at >= start_date, Order.created_at <= end_date_filter)
     
    if user_id:
        top_selling_products_query = top_selling_products_query.filter(Order.user_id == user_id)
        
    top_selling_products = top_selling_products_query.group_by(Product.name)\
     .order_by(sqlalchemy.text('total_qty DESC'))\
     .limit(10).all()

    # 8. Waiter/User Performance Breakdown
    from app.models.payment import Payment
    from app.models.user import User as UserModel

    # Using aggregation to avoid N+1 slow queries
    waiter_stats_query = db.session.query(
        UserModel.username,
        UserModel.role,
        sqlalchemy.func.sum(Order.total_amount).label('total'),
        sqlalchemy.func.sum(Order.amount_due).label('debt')
    ).join(Order, Order.user_id == UserModel.id)\
     .filter(Order.created_at >= start_date, Order.created_at <= end_date_filter)

    if current_user.role not in ('admin', 'manager'):
        waiter_stats_query = waiter_stats_query.filter(UserModel.id == current_user.id)
    
    waiter_totals = waiter_stats_query.group_by(UserModel.id).all()

    # Get Payment breakdown for these users in two queries (one for each method)
    # This is much faster than querying per user
    payment_breakdown = db.session.query(
        Order.user_id,
        Payment.payment_method,
        sqlalchemy.func.sum(Payment.amount)
    ).join(Payment, Payment.order_id == Order.id)\
     .filter(Order.created_at >= start_date, Order.created_at <= end_date_filter)\
     .group_by(Order.user_id, Payment.payment_method).all()

    # Map payment breakdown to a dictionary for easy access
    pay_map = {}
    for uid, method, amt in payment_breakdown:
        if uid not in pay_map: pay_map[uid] = {}
        pay_map[uid][method] = float(amt or 0)

    waiter_stats = []
    # We need to re-fetch active_users to get IDs correctly for mapping
    # OR we can just use the query above if we include the ID
    final_query = db.session.query(
        UserModel.id, UserModel.username, UserModel.role,
        sqlalchemy.func.sum(Order.total_amount),
        sqlalchemy.func.sum(Order.amount_due)
    ).join(Order, Order.user_id == UserModel.id)\
     .filter(Order.created_at >= start_date, Order.created_at <= end_date_filter)
    
    if current_user.role not in ('admin', 'manager'):
        final_query = final_query.filter(UserModel.id == current_user.id)
        
    results = final_query.group_by(UserModel.id).all()

    for uid, username, role, total, debt in results:
        m_pays = pay_map.get(uid, {})
        waiter_stats.append({
            'username': username,
            'role': role,
            'evc': m_pays.get('EVC Plus', 0.0),
            'edahab': m_pays.get('eDahab', 0.0),
            'cash': m_pays.get('Cash', 0.0),
            'debt': float(debt or 0),
            'total': float(total or 0)
        })

    # Calculate Grand Totals for Waiters
    waiter_grand_totals = {
        'evc': sum(s['evc'] for s in waiter_stats),
        'edahab': sum(s['edahab'] for s in waiter_stats),
        'cash': sum(s['cash'] for s in waiter_stats),
        'debt': sum(s['debt'] for s in waiter_stats),
        'total': sum(s['total'] for s in waiter_stats)
    }

    return render_template('reports/index.html', 
                          total_revenue=total_revenue,
                          total_orders=total_orders,
                          total_products=total_products,
                          revenue_by_status=revenue_by_status,
                          start_date=start_date.strftime('%Y-%m-%d'),
                          end_date=end_date.strftime('%Y-%m-%d'),
                          estimated_cogs=estimated_cogs,
                          gross_profit=gross_profit,
                          apportioned_salaries=apportioned_salaries,
                          total_expenses=total_expenses,
                          net_profit=net_profit,
                          users=users,
                          selected_user_id=user_id,
                          daily_revenue=daily_revenue,
                          daily_labels=daily_labels,
                          order_type_stats=order_type_stats,
                          top_selling_products=top_selling_products,
                          waiter_stats=waiter_stats,
                          waiter_grand_totals=waiter_grand_totals)


@reports_bp.route('/audit')
@login_required
@manager_required
def audit():
    from app.models.audit_log import AuditLog
    # Automatically cleanup logs older than 5 days
    AuditLog.cleanup(days=5)
    
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    return render_template('reports/audit.html', logs=logs)

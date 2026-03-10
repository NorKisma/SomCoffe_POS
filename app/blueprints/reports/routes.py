from flask import render_template, request
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
def index():
    # Date Filtering
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    user_id = request.args.get('user_id', type=int)
    
    today = datetime.now()
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        # Default to first day of the current month
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        end_date = today

    # Prepare query filters for the date range
    # End date should include the whole day (up to 23:59:59)
    end_date_filter = end_date + timedelta(days=1) - timedelta(microseconds=1)

    # Base Order Query
    orders_query = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date_filter
    )
    
    if user_id:
        orders_query = orders_query.filter(Order.user_id == user_id)
    
    # Calculate revenue (Only completed and paid orders for P&L)
    completed_orders = orders_query.filter(Order.status == 'completed')
    
    total_revenue_query = db.session.query(sqlalchemy.func.sum(Order.total_amount)).filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date_filter,
        Order.status == 'completed'
    )
    
    if user_id:
        total_revenue_query = total_revenue_query.filter(Order.user_id == user_id)
        
    total_revenue = total_revenue_query.scalar() or 0.0

    total_orders = orders_query.count()
    total_products = Product.query.count()
    
    # Revenue per status (All statuses for the chart/breakdown)
    revenue_by_status_query = db.session.query(
        Order.status, sqlalchemy.func.sum(Order.total_amount)
    ).filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date_filter
    ).group_by(Order.status)
    
    if user_id:
        revenue_by_status_query = revenue_by_status_query.filter(Order.user_id == user_id)
        
    revenue_by_status = revenue_by_status_query.all()
    
    # === PROFIT & LOSS CALCULATIONS ===
    # 1. Estimated COGS (Cost of goods sold) - Typically 30% for restaurants
    estimated_cogs = float(total_revenue) * 0.30
    
    # 2. Gross Profit
    gross_profit = float(total_revenue) - estimated_cogs
    
    # 3. Staff Salaries
    # We apportion the monthly salaries to the days in the date range.
    days_in_range = max((end_date.date() - start_date.date()).days + 1, 1)
    # Sum of all monthly salaries
    total_monthly_salaries = db.session.query(sqlalchemy.func.sum(Employee.salary)).scalar() or 0.0
    # Approximate daily salary cost * days in range
    apportioned_salaries = (float(total_monthly_salaries) / 30.0) * days_in_range
    
    # 4. Other Expenses
    total_expenses = db.session.query(sqlalchemy.func.sum(Expense.amount)).filter(
        Expense.date >= start_date.date(),
        Expense.date <= end_date.date()
    ).scalar() or 0.0
    
    # 5. Net Profit
    net_profit = gross_profit - apportioned_salaries - float(total_expenses)

    # Fetch users for filter (Waiters & Cashiers)
    users = User.query.all()

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
                          selected_user_id=user_id)


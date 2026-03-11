from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.extensions.db import db
from app.models.customer import Customer
from app.models.order import Order
from app.utils.decorators import admin_required
from . import customers_bp

@customers_bp.route('/')
@login_required
def index():
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('customers/index.html', customers=customers)

@customers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        credit_limit = float(request.form.get('credit_limit') or 0.0)

        if not name:
            flash('Customer name is required', 'danger')
            return redirect(url_for('customers.add'))

        customer = Customer(
            name=name,
            phone=phone,
            email=email,
            address=address,
            credit_limit=credit_limit
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully', 'success')
        return redirect(url_for('customers.index'))

    return render_template('customers/add.html')

@customers_bp.route('/<int:customer_id>')
@login_required
def view(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    
    # Calculate outstanding balance for credit sales
    # Orders where payment_status is not 'paid'
    outstanding_orders = Order.query.filter(
        Order.customer_id == customer_id, 
        Order.payment_status != 'paid'
    ).all()
    
    balance = sum(o.total_amount for o in outstanding_orders)
    
    return render_template('customers/view.html', customer=customer, orders=orders, balance=balance)

@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.phone = request.form.get('phone')
        customer.email = request.form.get('email')
        customer.address = request.form.get('address')
        customer.credit_limit = float(request.form.get('credit_limit') or 0.0)

        if not customer.name:
            flash('Customer name is required', 'danger')
            return redirect(url_for('customers.edit', customer_id=customer.id))

        db.session.commit()
        flash('Customer updated successfully', 'success')
        return redirect(url_for('customers.view', customer_id=customer.id))

    return render_template('customers/edit.html', customer=customer)

@customers_bp.route('/<int:customer_id>/statement')
@login_required
def statement(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    
    # Calculate outstanding balance
    outstanding_orders = Order.query.filter(
        Order.customer_id == customer_id, 
        Order.payment_status != 'paid'
    ).all()
    balance = sum(o.total_amount for o in outstanding_orders)
    
    from app.models.setting import Setting
    settings = {s.key: s.value for s in Setting.query.all()}
    
    from datetime import datetime
    return render_template('customers/statement.html', 
                           customer=customer, 
                           orders=orders, 
                           balance=balance,
                           now=datetime.utcnow(),
                           sys_name=settings.get('system_name', 'SomCoffe POS'),
                           sys_address=settings.get('address', ''),
                           sys_phone=settings.get('phone', ''))

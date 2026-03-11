from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from app.extensions.db import db
from app.models.customer import Customer
from app.models.order import Order
from app.models.payment import Payment
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

    outstanding_orders = Order.query.filter(
        Order.customer_id == customer_id,
        Order.payment_status != 'paid'
    ).all()

    balance = customer.current_debt

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

    outstanding_orders = Order.query.filter(
        Order.customer_id == customer_id,
        Order.payment_status != 'paid'
    ).all()
    
    balance = customer.current_debt

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


@customers_bp.route('/<int:customer_id>/pay', methods=['POST'])
@login_required
def record_payment(customer_id):
    """Record a payment against a customer's outstanding debt (oldest-first)."""
    customer = Customer.query.get_or_404(customer_id)

    try:
        amount_paid = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method', 'Cash')
    except (ValueError, TypeError):
        flash('Xaaladda khaldan. Fadlan geli lacag saxsan.', 'danger')
        return redirect(url_for('customers.view', customer_id=customer_id))

    if amount_paid <= 0:
        flash('Lacagta waa inay ka weyn tahay eber.', 'danger')
        return redirect(url_for('customers.view', customer_id=customer_id))

    # Get all unpaid / partial orders, oldest-first
    unpaid_orders = Order.query.filter(
        Order.customer_id == customer_id,
        Order.payment_status != 'paid'
    ).order_by(Order.created_at.asc()).all()

    total_debt = customer.current_debt

    if amount_paid > total_debt:
        flash(
            f'Lacagta aad gelisay ({amount_paid:,.2f}) waxay ka weyn tahay deynta ({total_debt:,.2f}).',
            'warning'
        )
        return redirect(url_for('customers.view', customer_id=customer_id))

    remaining = amount_paid

    for order in unpaid_orders:
        if remaining <= 0:
            break

        already_paid = sum(p.amount for p in order.payments)
        still_owed = order.total_amount - already_paid

        if still_owed <= 0:
            order.payment_status = 'paid'
            continue

        if remaining >= still_owed:
            # Fully cover this order
            pay = Payment(
                amount=still_owed,
                payment_method=payment_method,
                order_id=order.id
            )
            db.session.add(pay)
            order.payment_status = 'paid'
            remaining -= still_owed
        else:
            # Partial payment
            pay = Payment(
                amount=remaining,
                payment_method=payment_method,
                order_id=order.id
            )
            db.session.add(pay)
            order.payment_status = 'partial'
            remaining = 0

    db.session.commit()
    flash(
        f'Lacag-bixinta ${amount_paid:,.2f} si guul leh ayaa loo diiwaan-geliyay!',
        'success'
    )
    return redirect(url_for('customers.view', customer_id=customer_id))

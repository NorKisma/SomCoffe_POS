from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import orders_bp
from app.services.order_service import OrderService
from app.extensions import db

from app.utils.decorators import admin_required, waiter_required, manager_required, cashier_required

@orders_bp.route('/')
@login_required
@waiter_required
def index():
    from app.models.order import Order
    # Filter orders: waiters only see their own orders. Cashiers/Managers/Admins see all.
    if current_user.role == 'waiter':
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('orders/index.html', orders=orders)

@orders_bp.route('/view/<int:id>', methods=['GET'])
@login_required
@waiter_required
def view_order(id):
    try:
        details = OrderService.get_order_details(id)
        return jsonify({'success': True, 'data': details})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
@manager_required
def edit_order(id):
    status = request.form.get('status')
    customer_name = request.form.get('customer_name')
    
    try:
        OrderService.update_order(id, status, customer_name)
        flash('Order updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating order: {str(e)}', 'danger')
        
    return redirect(url_for('orders.index'))

@orders_bp.route('/print/<int:id>')
@login_required
@waiter_required
def print_receipt(id):
    try:
        from app.models.order import Order
        order_exists = db.session.get(Order, id)
        if not order_exists:
            flash(f'Cillad: Dalabka lama helin (Order #{id} not found in database).', 'danger')
            return redirect(url_for('orders.index'))
            
        details = OrderService.get_order_details(id)
        return render_template('orders/receipt.html', order=details)
    except Exception as e:
        flash(f'Error generating receipt: {str(e)}', 'danger')
        return redirect(url_for('orders.index'))

@orders_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@manager_required
def delete_order(id):
    try:
        from app.models.order import Order
        order = Order.query.get(id)
        if not order:
            return jsonify({'success': False, 'message': 'Dalabka lama helin (Order not found)'}), 404
        
        # Restore stock
        for item in order.items:
            product = item.product
            if product and getattr(product, 'stock', None) is not None and not getattr(product, 'is_service', False):
                product.stock += item.quantity
        
        db.session.delete(order)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dalabka si guul leh ayaa loo tirtiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Cillad dhidhibada ah: {str(e)}'}), 500

@orders_bp.route('/clear-all', methods=['POST'])
@login_required
@admin_required
def clear_all_orders():
    try:
        from app.models.order import Order
        orders = Order.query.all()
        for order in orders:
            for item in order.items:
                product = item.product
                if product and getattr(product, 'stock', None) is not None and not getattr(product, 'is_service', False):
                    product.stock += item.quantity
            db.session.delete(order)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dhamaan dalabyada waa la tir-tiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Cillad wadar ah: {str(e)}'}), 500

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from . import orders_bp
from app.services.order_service import OrderService

@orders_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = OrderService.get_paginated_orders(page=page, per_page=10)
    orders = pagination.items
    return render_template('orders/index.html', orders=orders, pagination=pagination)

@orders_bp.route('/view/<int:id>', methods=['GET'])
@login_required
def view_order(id):
    try:
        details = OrderService.get_order_details(id)
        return jsonify({'success': True, 'data': details})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
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
def print_receipt(id):
    try:
        details = OrderService.get_order_details(id)
        return render_template('orders/receipt.html', order=details)
    except Exception as e:
        flash(f'Error generating receipt: {str(e)}', 'danger')
        return redirect(url_for('orders.index'))

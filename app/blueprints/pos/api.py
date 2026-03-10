from flask import request, jsonify
from flask_login import login_required, current_user
from app.services.pos_service import POSService
from app.models.customer import Customer
from app.extensions.db import db
from app.utils.decorators import waiter_required
from . import pos_bp

@pos_bp.route('/checkout', methods=['POST'])
@login_required
@waiter_required
def checkout():
    data = request.get_json()
    items = data.get('items', [])
    table_id = data.get('table_id')
    payment_method = data.get('payment_method', 'Pending')
    customer_id = data.get('customer_id')
    split_payment = data.get('split_payment')
    order_id = data.get('order_id')
    
    # RBAC: Waiter cannot process final payments
    if current_user.role == 'waiter' and payment_method != 'Pending':
        return jsonify({'success': False, 'message': 'Waiters cannot process final payments.'}), 403
    
    if not items:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
    try:
        new_order = POSService.create_order(items, table_id, current_user.id, payment_method, customer_id, split_payment, order_id)
        return jsonify({'success': True, 'order_id': new_order.id})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@pos_bp.route('/add_customer', methods=['POST'])
@login_required
@waiter_required
def add_customer():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    
    if not name:
        return jsonify({'success': False, 'message': 'Customer name is required'}), 400
        
    try:
        customer = Customer(name=name, phone=phone)
        db.session.add(customer)
        db.session.commit()
        return jsonify({
            'success': True, 
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone or ''
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
@pos_bp.route('/check_table/<int:table_id>', methods=['GET'])
@login_required
@waiter_required
def check_table(table_id):
    order = POSService.get_active_order_for_table(table_id)
    if order:
        return jsonify({
            'exists': True,
            'order_id': order.id,
            'total': order.total_amount,
            'items': [{'id': i.product.id, 'name': i.product.name, 'qty': i.quantity, 'price': i.price_at_time} for i in order.items]
        })
    return jsonify({'exists': False})

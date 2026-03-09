from flask import render_template, request, jsonify
from flask_login import current_user, login_required
from . import pos_bp
from app.models.product import Product
from app.models.category import Category
from app.models.table import Table
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.setting import Setting
from app.extensions.db import db
from datetime import datetime

@pos_bp.route('/')
@login_required
def index():
    from app.models.customer import Customer
    products = Product.query.all()
    categories = Category.query.all()
    tables = Table.query.all()
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('pos/pos.html', products=products, categories=categories, tables=tables, customers=customers)

from app.services.pos_service import POSService

@pos_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()
    items = data.get('items', [])
    table_id = data.get('table_id')
    payment_method = data.get('payment_method', 'Pending')
    customer_id = data.get('customer_id')
    
    if not items:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
    try:
        new_order = POSService.create_order(items, table_id, current_user.id, payment_method, customer_id)
        return jsonify({'success': True, 'order_id': new_order.id})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
@pos_bp.route('/add_customer', methods=['POST'])
@login_required
def add_customer():
    from app.models.customer import Customer
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

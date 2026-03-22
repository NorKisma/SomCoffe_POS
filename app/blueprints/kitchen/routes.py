from flask import render_template, jsonify, flash, redirect, url_for
from flask_login import login_required
from . import kitchen_bp
from app.models.order import Order
from app.extensions.db import db
from datetime import datetime, timedelta

@kitchen_bp.route('/')
@login_required
def index():
    # Auto-complete orders older than 5 minutes
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    old_orders = Order.query.filter(Order.status == 'pending', Order.created_at <= five_min_ago).all()
    if old_orders:
        for oo in old_orders:
            oo.status = 'completed'
        db.session.commit()
    
    # Show active orders (pending)
    pending_orders = Order.query.filter_by(status='pending').order_by(Order.created_at.asc()).all()
    return render_template('kitchen/index.html', orders=pending_orders)

@kitchen_bp.route('/complete/<int:order_id>', methods=['POST'])
@login_required
def complete_order(order_id):
    order = db.session.get(Order, order_id)
    if order:
        order.status = 'completed'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Order not found'}), 404

@kitchen_bp.route('/api/pending')
@login_required
def get_pending_api():
    # Auto-complete orders older than 5 minutes
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    old_orders = Order.query.filter(Order.status == 'pending', Order.created_at <= five_min_ago).all()
    if old_orders:
        for oo in old_orders:
            oo.status = 'completed'
        db.session.commit()

    orders = Order.query.filter_by(status='pending').order_by(Order.created_at.asc()).all()
    data = []
    for o in orders:
        data.append({
            'id': o.id,
            'table': o.table.number if o.table else 'Takeaway',
            'time': o.created_at.strftime('%H:%M'),
            'elapsed': int((datetime.utcnow() - o.created_at).total_seconds() / 60),
            'items': [{'name': i.product.name, 'qty': i.quantity} for i in o.items]
        })
    return jsonify(data)

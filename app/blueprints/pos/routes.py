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

from app.utils.decorators import waiter_required

@pos_bp.route('/')
@login_required
@waiter_required
def index():
    from app.models.customer import Customer
    products = Product.query.all()
    categories = Category.query.all()
    tables = Table.query.all()
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('pos/pos.html', products=products, categories=categories, tables=tables, customers=customers)

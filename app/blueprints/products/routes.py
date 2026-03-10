import os
from flask import render_template, request, redirect, url_for, flash, current_app
from . import products_bp
from app.models.product import Product
from app.models.category import Category
from app.extensions.db import db
from app.services.product_service import ProductService
from app.services.category_service import CategoryService

@products_bp.route('/')
def index():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('products/products.html', products=products, categories=categories)

@products_bp.route('/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    price = float(request.form.get('price'))
    category_id = int(request.form.get('category_id'))
    stock = int(request.form.get('stock', 0))
    is_service = True if request.form.get('is_service') else False
    file = request.files.get('image')
    
    ProductService.create_product(name, price, category_id, stock, is_service, file)
    
    flash(f'Alaabta {name} si guul leh ayaa loogu daray!', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/edit/<int:id>', methods=['POST'])
def edit_product(id):
    name = request.form.get('name')
    price = float(request.form.get('price'))
    category_id = int(request.form.get('category_id'))
    stock = int(request.form.get('stock', 0))
    is_service = True if request.form.get('is_service') else False
    file = request.files.get('image')
    
    ProductService.update_product(id, name, price, category_id, stock, is_service, file)
    
    flash(f'Alaabta {name} si guul leh ayaa loo beddelay!', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    ProductService.delete_product(id)
    flash('Alaabta waa laga saaray!', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/add-category', methods=['POST'])
def add_category():
    name = request.form.get('name')
    icon = request.form.get('icon', 'tag')
    file = request.files.get('image')
    
    if not name:
        flash('Magaca category-ga waa muhiim!', 'danger')
        return redirect(url_for('products.index'))
        
    _, error = CategoryService.create_category(name, icon, file)
    if error:
        flash(error, 'danger')
    else:
        flash(f'Category-ga {name} waa la abuuray!', 'success')
        
    return redirect(url_for('products.index'))

@products_bp.route('/delete-category/<int:id>', methods=['POST'])
def delete_category(id):
    success, error = CategoryService.delete_category(id)
    if error:
        flash(error, 'danger')
    else:
        flash('Category-ga waa la saaray!', 'success')
        
    return redirect(url_for('products.index'))

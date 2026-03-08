from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from . import users_bp
from app.services.user_service import UserService

@users_bp.route('/')
@login_required
@admin_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = UserService.get_paginated_users(page=page, per_page=10)
    users = pagination.items
    return render_template('users/index.html', users=users, pagination=pagination)

@users_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'staff')
    
    _, error = UserService.create_user(username, email, password, role)
    if error:
        flash(error, 'danger')
    else:
        flash('User added successfully!', 'success')
        
    return redirect(url_for('users.index'))

@users_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    success, error = UserService.delete_user(id, current_user.id)
    if error:
        flash(error, 'danger')
    else:
        flash('User deleted successfully!', 'success')
        
    return redirect(url_for('users.index'))

@users_bp.route('/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_user(id):
    email = request.form.get('email')
    role = request.form.get('role')
    
    UserService.update_user(id, email, role)
    
    flash('User updated!', 'success')
    return redirect(url_for('users.index'))

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import admin_required, manager_required
from . import users_bp
from app.services.user_service import UserService

@users_bp.route('/')
@login_required
@manager_required
def index():
    from app.models.user import User
    users = User.query.all()
    return render_template('users/index.html', users=users)

@users_bp.route('/add', methods=['POST'])
@login_required
@manager_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'waiter')
    evc_number = request.form.get('evc_number')
    edahab_number = request.form.get('edahab_number')
    pin = request.form.get('pin')
    
    # Security: Non-admins cannot create Admin accounts
    if role == 'admin' and not current_user.is_admin:
        flash('Action Denied: You do not have permission to create Admin accounts.', 'danger')
        return redirect(url_for('users.index'))
    
    _, error = UserService.create_user(username, email, password, role, evc_number, edahab_number, pin)
    if error:
        flash(error, 'danger')
    else:
        flash('User added successfully!', 'success')
        
    return redirect(url_for('users.index'))

@users_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@manager_required
def delete_user(id):
    success, error = UserService.delete_user(id, current_user.id)
    if error:
        flash(error, 'danger')
    else:
        flash('User deleted successfully!', 'success')
        
    return redirect(url_for('users.index'))

@users_bp.route('/update/<int:id>', methods=['POST'])
@login_required
@manager_required
def update_user(id):
    from app.models.user import User
    target_user = User.query.get_or_404(id)
    
    # Security: Admin accounts can ONLY be updated by themselves
    if target_user.role == 'admin':
        if current_user.id != target_user.id:
            flash('Security Violation: Admin accounts can only be updated by the owner.', 'danger')
            return redirect(url_for('users.index'))
        
    # Security: Managers cannot promote someone to Admin
    role = request.form.get('role')
    if role == 'admin' and not current_user.is_admin:
        flash('Action Denied: You do not have permission to assign Admin role.', 'danger')
        return redirect(url_for('users.index'))

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    evc_number = request.form.get('evc_number')
    edahab_number = request.form.get('edahab_number')
    pin = request.form.get('pin')
    
    user, error = UserService.update_user(id, username, email, role, password, evc_number, edahab_number, pin)
    
    if error:
        flash(error, 'danger')
    else:
        flash('User updated successfully!', 'success')
        
    return redirect(url_for('users.index'))

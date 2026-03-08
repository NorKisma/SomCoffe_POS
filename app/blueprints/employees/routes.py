from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from . import employees_bp
from app.models.employee import Employee
from app.models.user import User
from app.extensions.db import db

@employees_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Employee.query.paginate(page=page, per_page=10, error_out=False)
    employees = pagination.items
    
    # Also fetch users to link to (excluding those already linked)
    users = User.query.filter(~User.employee.has()).all()
    return render_template('employees/index.html', employees=employees, users=users, pagination=pagination)

@employees_bp.route('/add', methods=['POST'])
@login_required
def add():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    position = request.form.get('position')
    phone = request.form.get('phone')
    salary = request.form.get('salary', 0.0)
    user_id = request.form.get('user_id')
    
    new_emp = Employee(
        first_name=first_name,
        last_name=last_name,
        position=position,
        phone=phone,
        salary=float(salary) if salary else 0.0,
        user_id=int(user_id) if user_id and user_id != 'None' else None
    )
    
    db.session.add(new_emp)
    db.session.commit()
    flash('New employee registered successfully!', 'success')
    return redirect(url_for('employees.index'))

@employees_bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    emp = Employee.query.get_or_404(id)
    emp.first_name = request.form.get('first_name')
    emp.last_name = request.form.get('last_name')
    emp.position = request.form.get('position')
    emp.phone = request.form.get('phone')
    emp.salary = float(request.form.get('salary', 0.0))
    emp.status = request.form.get('status', 'active')
    
    db.session.commit()
    flash('Employee record updated!', 'success')
    return redirect(url_for('employees.index'))

@employees_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    flash('Employee record deleted!', 'info')
    return redirect(url_for('employees.index'))

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import expenses_bp
from app.extensions import db
from app.models.expense import Expense
from datetime import datetime
from app.utils.decorators import manager_required

@expenses_bp.route('/')
@login_required
@manager_required
def index():
    expenses = Expense.query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    return render_template('expenses/index.html', expenses=expenses)

@expenses_bp.route('/add', methods=['POST'])
@login_required
@manager_required
def add_expense():
    description = request.form.get('description')
    amount = request.form.get('amount')
    date_str = request.form.get('date')
    category = request.form.get('category')
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        expense = Expense(
            description=description,
            amount=float(amount),
            date=date_obj,
            category=category,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Kharaashka (Expense) si guul leh ayaa loo diiwaangeliyay!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Cillad ayaa dhacday: {str(e)}', 'danger')
        
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
@manager_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    expense.description = request.form.get('description')
    expense.amount = float(request.form.get('amount'))
    expense.category = request.form.get('category')
    
    date_str = request.form.get('date')
    if date_str:
        expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
    try:
        db.session.commit()
        flash('Kharaashka waa la cusboonaysiiyay!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Cillad ayaa dhacday: {str(e)}', 'danger')
        
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@manager_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    try:
        db.session.delete(expense)
        db.session.commit()
        flash('Kharaashka waa la tirtiray!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Cillad ayaa dhacday: {str(e)}', 'danger')
        
    return redirect(url_for('expenses.index'))

from flask import render_template, redirect, url_for, flash, request, session
from flask_babel import _
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from app.models.user import User
from app.extensions.db import db
from app.extensions.mail import mail
from flask_mail import Message
import random
from datetime import datetime, timedelta

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(_('You have logged in successfully!'), 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(_('Invalid username or password!'), 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have logged out successfully!'), 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            otp = str(random.randint(100000, 999999))
            user.reset_otp = otp
            user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=10)
            db.session.commit()
            
            # Send Email
            try:
                msg = Message(_('Your OTP Code'),
                            sender=None, # Uses default from config
                            recipients=[email])
                msg.body = _("Your password reset code is: %(otp)s. Valid for 10 minutes.", otp=otp)
                mail.send(msg)
                
                session['reset_email'] = email
                flash(_('OTP code has been sent to your email.'), 'success')
                return redirect(url_for('auth.verify_otp'))
            except Exception as e:
                flash(_('Error sending email: %(error)s', error=str(e)), 'danger')
        else:
            flash(_('Email (%(email)s) not found in the system!', email=email), 'danger')
            
    return render_template('auth/forgot_password.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        otp = request.form.get('otp')
        email = session['reset_email']
        user = User.query.filter_by(email=email, reset_otp=otp).first()
        
        if user and user.reset_otp_expiry > datetime.utcnow():
            session['otp_verified'] = True
            return redirect(url_for('auth.reset_password'))
        else:
            flash(_('Invalid or expired OTP code!'), 'danger')
            
    return render_template('auth/verify_otp.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified') or 'reset_email' not in session:
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash(_('Passwords do not match!'), 'danger')
            return render_template('auth/reset_password.html')
            
        email = session['reset_email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.set_password(password)
            user.reset_otp = None
            user.reset_otp_expiry = None
            db.session.commit()
            
            session.pop('reset_email', None)
            session.pop('otp_verified', None)
            
            flash(_('Your password has been reset successfully!'), 'success')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/reset_password.html')
@auth_bp.route('/verify-pin', methods=['POST'])
@login_required
def verify_pin():
    pin = request.form.get('pin')
    if current_user.pin == pin:
        return {'success': True}
    return {'success': False, 'message': _('Incorrect PIN!')}, 401

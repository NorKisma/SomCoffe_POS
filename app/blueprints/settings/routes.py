from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.utils.decorators import admin_required
from . import settings_bp
from app.models.setting import Setting

@settings_bp.route('/')
@login_required
@admin_required
def index():
    # Fetch real settings from database
    settings = {
        'restaurant_name': Setting.get_val('restaurant_name', 'Rays POS & Restaurant'),
        'vat_rate': Setting.get_val('vat_rate', '0'),
        'currency': Setting.get_val('currency', '$'),
        'address': Setting.get_val('address', 'Mogadishu, Somalia'),
        'phone': Setting.get_val('phone', '+252 61 0000000'),
        'auto_logout': Setting.get_val('auto_logout', 'OFF'),
        'session_timeout': Setting.get_val('session_timeout', '5')
    }
    return render_template('settings/index.html', settings=settings)

@settings_bp.route('/update', methods=['POST'])
@login_required
@admin_required
def update():
    keys = ['restaurant_name', 'vat_rate', 'currency', 'address', 'phone', 'auto_logout', 'session_timeout']
    for key in keys:
        val = request.form.get(key)
        if val is not None:
            Setting.set_val(key, val)
            
    flash('System configuration updated successfully!', 'success')
    return redirect(url_for('settings.index'))

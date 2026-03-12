from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.utils.decorators import admin_required
from . import settings_bp
from app.models.setting import Setting

@settings_bp.route('/')
@login_required
@admin_required
def index():
    import time
    # Fetch real settings from database
    settings = {
        'restaurant_name': Setting.get_val('restaurant_name', 'Rays POS & Restaurant'),
        'vat_rate': Setting.get_val('vat_rate', '0'),
        'currency': Setting.get_val('currency', '$'),
        'address': Setting.get_val('address', 'Mogadishu, Somalia'),
        'phone': Setting.get_val('phone', '+252 61 0000000'),
        'auto_logout': Setting.get_val('auto_logout', 'OFF'),
        'session_timeout': Setting.get_val('session_timeout', '5'),
        'evc_number': Setting.get_val('evc_number', ''),
        'edahab_number': Setting.get_val('edahab_number', '')
    }
    
    # Simple dynamic health check
    try:
        start_time = time.time()
        Setting.query.first()
        db_status = "STABLE"
        resp_time = f"{int((time.time() - start_time) * 1000)}ms"
    except:
        db_status = "ERROR"
        resp_time = "N/A"

    return render_template('settings/index.html', settings=settings, db_status=db_status, resp_time=resp_time)

@settings_bp.route('/update', methods=['POST'])
@login_required
@admin_required
def update():
    from app.models.audit_log import AuditLog
    keys = ['restaurant_name', 'vat_rate', 'currency', 'address', 'phone', 'auto_logout', 'session_timeout', 'evc_number', 'edahab_number']
    changes = []
    
    for key in keys:
        old_val = Setting.get_val(key)
        new_val = request.form.get(key)
        
        if new_val is not None and new_val != old_val:
            Setting.set_val(key, new_val)
            changes.append(f"{key}: {old_val} -> {new_val}")
            
    if changes:
        AuditLog.log('UPDATE_SETTINGS', f"Updated values: {', '.join(changes)}")
            
    flash('System configuration updated successfully!', 'success')
    return redirect(url_for('settings.index'))

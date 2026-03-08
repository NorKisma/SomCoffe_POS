from flask import render_template
from . import dashboard_bp

@dashboard_bp.route('/')
def index():
    return render_template('dashboard/dashboard.html')

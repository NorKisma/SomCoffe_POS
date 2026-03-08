from flask import Blueprint

employees_bp = Blueprint('employees', __name__, template_folder='templates')

from . import routes
    

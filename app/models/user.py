from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Roles: admin | manager | cashier | waiter
    role = db.Column(db.String(20), default='waiter')
    evc_number = db.Column(db.String(20), nullable=True)
    edahab_number = db.Column(db.String(20), nullable=True)
    pin = db.Column(db.String(10), nullable=True) # Staff PIN access
    reset_otp = db.Column(db.String(6), nullable=True)
    reset_otp_expiry = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ── Role helpers (use in templates & decorators) ──────────
    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager_or_above(self):
        return self.role in ('admin', 'manager')

    @property
    def is_cashier_or_above(self):
        return self.role in ('admin', 'manager', 'cashier')

    @property
    def is_waiter_or_above(self):
        return self.role in ('admin', 'manager', 'cashier', 'waiter', 'kitchen')

    @property
    def is_kitchen(self):
        return self.role == 'kitchen'

    @property
    def role_label(self):
        labels = {
            'admin': 'Admin',
            'manager': 'Manager',
            'cashier': 'Cashier',
            'waiter': 'Waiter',
            'kitchen': 'Kitchen',
        }
        return labels.get(self.role, self.role.capitalize())

    @property
    def role_color(self):
        colors = {
            'admin': 'danger',
            'manager': 'primary',
            'cashier': 'success',
            'waiter': 'warning',
            'kitchen': 'info',
        }
        return colors.get(self.role, 'secondary')

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'

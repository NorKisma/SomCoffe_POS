from app.extensions.db import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False) # e.g., 'LOGIN', 'DELETE_ORDER', 'UPDATE_PRODUCT'
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'

    @staticmethod
    def log(action, description=None, user_id=None):
        from flask_login import current_user
        from flask import request
        
        uid = user_id or (current_user.id if current_user.is_authenticated else None)
        ip = request.remote_addr if request else None
        
        entry = AuditLog(
            user_id=uid,
            action=action,
            description=description,
            ip_address=ip
        )
        db.session.add(entry)
        db.session.commit()

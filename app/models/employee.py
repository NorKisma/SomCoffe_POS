from app.extensions.db import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    salary = db.Column(db.Float, default=0.0)
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active') # active, inactive
    
    # Optional: Link to a system User account if applicable
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('employee', uselist=False))

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'

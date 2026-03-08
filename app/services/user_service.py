from app.models.user import User
from app.extensions.db import db

class UserService:
    @staticmethod
    def get_paginated_users(page, per_page):
        return User.query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def create_user(username, email, password, role='staff'):
        if User.query.filter_by(username=username).first():
            return None, 'Username already exists!'
        
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        return new_user, None

    @staticmethod
    def delete_user(user_id, current_user_id):
        if user_id == current_user_id:
            return False, 'You cannot delete yourself!'
            
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return True, None

    @staticmethod
    def update_user(user_id, email, role):
        user = User.query.get_or_404(user_id)
        user.email = email
        user.role = role
        db.session.commit()
        return user, None

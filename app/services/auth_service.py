from app.models.user import User
from app.extensions.db import db
from flask_login import login_user, logout_user

class AuthService:
    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def login(user, remember=False):
        return login_user(user, remember=remember)

    @staticmethod
    def logout():
        logout_user()

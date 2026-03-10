import random
import string
from flask_mail import Message
from app.extensions.mail import mail
from flask import current_app

class AuthModuleService:
    @staticmethod
    def generate_otp(length=6):
        """Generates a random numeric OTP."""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def send_otp_email(email, otp):
        """Sends OTP to the user's email."""
        msg = Message('SomCoffe - Reset Your Password',
                      sender=current_app.config.get('MAIL_USERNAME'),
                      recipients=[email])
        msg.body = f"Your OTP code is: {otp}. It will expire in 10 minutes."
        try:
            mail.send(msg)
            return True
        except Exception:
            return False

from functools import wraps
from flask import abort, request
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

class Security:
    """
    General security functions, rate limiting, and extra validations.
    """
    
    @staticmethod
    def require_role(allowed_roles):
        """
        Decorator to restrict access based on user role list.
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    return abort(401)
                if current_user.role not in allowed_roles:
                    logger.warning(f"Unauthorized access attempt by {current_user.username} to {request.path}")
                    return abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @staticmethod
    def log_suspicious_activity(user_id, action, details):
        """
        Logging utility specifically for tracking suspicious behavior.
        """
        logger.warning(f"[SUSPICIOUS] User {user_id} performed '{action}'. Details: {details}")
        return True

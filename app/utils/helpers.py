import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class Helpers:
    @staticmethod
    def generate_unique_id():
        """
        Generate a URL-safe UUID.
        """
        return str(uuid.uuid4())

    @staticmethod
    def format_currency(amount, currency_symbol="$"):
        """
        Formats float into string prefixed with currency.
        """
        return f"{currency_symbol} {amount:,.2f}"

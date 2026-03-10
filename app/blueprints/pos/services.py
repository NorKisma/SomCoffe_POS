from app.models.product import Product
from app.models.setting import Setting

class POSModuleService:
    @staticmethod
    def calculate_totals(items):
        """Logic for tax, discount, and total calculation."""
        subtotal = sum(item['price'] * item['qty'] for item in items)
        vat_rate_val = Setting.get_val('vat_rate', '15')
        vat_rate = float(vat_rate_val) / 100
        tax = subtotal * vat_rate
        total = subtotal + tax
        return {
            'subtotal': subtotal,
            'tax': tax,
            'total': total
        }

    @staticmethod
    def validate_cart(items):
        """Validate if items exist and have enough stock."""
        for item in items:
            product = Product.query.get(item['id'])
            if not product:
                return False, f"Product {item['id']} not found."
            if not getattr(product, 'is_service', False) and (product.stock or 0) < item['qty']:
                return False, f"Insufficient stock for {product.name}."
        return True, ""

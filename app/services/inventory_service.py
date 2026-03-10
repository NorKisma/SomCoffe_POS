from app.models.product import Product
from app.models.category import Category
from app.extensions.db import db

class InventoryService:
    @staticmethod
    def get_all_products():
        return Product.query.all()

    @staticmethod
    def get_all_categories():
        return Category.query.all()

    @staticmethod
    def get_low_stock_products(threshold=10):
        return Product.query.filter(Product.stock <= threshold).all()

    @staticmethod
    def update_stock(product_id, quantity_change):
        product = db.session.get(Product, product_id)
        if product and not getattr(product, 'is_service', False) and product.stock is not None:
            product.stock += quantity_change
            db.session.commit()
            return True
        return False

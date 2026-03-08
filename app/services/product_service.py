import os
from werkzeug.utils import secure_filename
from app.models.product import Product
from app.extensions.db import db
from flask import current_app

class ProductService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    @staticmethod
    def create_product(name, price, category_id, stock, is_service, file=None):
        image_filename = None
        if file and file.filename != '' and ProductService.allowed_file(file.filename):
            image_filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'products', image_filename))
        
        new_product = Product(name=name, price=price, category_id=category_id, stock=stock, image=image_filename, is_service=is_service)
        db.session.add(new_product)
        db.session.commit()
        return new_product

    @staticmethod
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        if product.image:
            try:
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'products', product.image))
            except:
                pass
        db.session.delete(product)
        db.session.commit()
        return True

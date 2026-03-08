import os
from werkzeug.utils import secure_filename
from app.models.category import Category
from app.models.product import Product
from app.extensions.db import db
from flask import current_app

class CategoryService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    @staticmethod
    def create_category(name, icon, file=None):
        existing = Category.query.filter_by(name=name).first()
        if existing:
            return None, 'Category-gan horey ayuu u jiray!'

        image_filename = None
        if file and file.filename != '' and CategoryService.allowed_file(file.filename):
            image_filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'categories', image_filename))

        new_cat = Category(name=name, icon=icon, image=image_filename)
        db.session.add(new_cat)
        db.session.commit()
        return new_cat, None

    @staticmethod
    def delete_category(category_id):
        category = Category.query.get_or_404(category_id)
        if Product.query.filter_by(category_id=category_id).first():
            return False, 'Ma tirtiri kartid category leh alaabo firfircoon!'
            
        if category.image:
            try:
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'categories', category.image))
            except:
                pass
                
        db.session.delete(category)
        db.session.commit()
        return True, None

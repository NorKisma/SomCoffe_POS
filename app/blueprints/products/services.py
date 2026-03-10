import os
from flask import current_app
from werkzeug.utils import secure_filename

class ProductsModuleService:
    @staticmethod
    def allowed_file(filename):
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        return '.' in filename and filename.split('.')[-1].lower() in allowed_extensions

    @staticmethod
    def save_image(file, subfolder='products'):
        """Method to save a product/category image and return the filename."""
        if file and ProductsModuleService.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
                
            file.save(os.path.join(upload_dir, filename))
            return filename
        return None

from app import create_app
from app.models.product import Product
app = create_app()
with app.app_context():
    for p in Product.query.all():
        print(f"{p.name} --> {p.category.name if p.category else 'No Category'}")

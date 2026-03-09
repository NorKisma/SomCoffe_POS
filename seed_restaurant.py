from app import create_app
from app.extensions.db import db
from app.models.category import Category
from app.models.table import Table
from app.models.product import Product
from app.models.user import User
from app.models.setting import Setting

app = create_app()

with app.app_context():
    # 1. Add Categories
    if not Category.query.first():
        cats = [
            Category(name='Coffee', icon='coffee'),
            Category(name='Tea', icon='leaf'),
            Category(name='Pastry', icon='croissant'),
            Category(name='Juice', icon='glass-water'),
            Category(name='Meals', icon='utensils')
        ]
        db.session.add_all(cats)
        db.session.commit()
        print("Categories seeded!")

    # 2. Add Tables
    if not Table.query.first():
        tables = [Table(number=f'Table {i}', capacity=4) for i in range(1, 13)]
        db.session.add_all(tables)
        db.session.commit()
        print("Tables seeded!")

    # 3. Add Some Products if empty
    if not Product.query.first():
        coffee_cat = Category.query.filter_by(name='Coffee').first()
        meal_cat = Category.query.filter_by(name='Meals').first()
        
        if coffee_cat and meal_cat:
            prods = [
                Product(name='Cappuccino', price=3.5, stock=50, category_id=coffee_cat.id),
                Product(name='Espresso', price=2.0, stock=100, category_id=coffee_cat.id),
                Product(name='Chicken Wrap', price=6.5, stock=20, category_id=meal_cat.id)
            ]
            db.session.add_all(prods)
            db.session.commit()
            print("Products seeded!")

    # 4. Add Admin User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='raystechcenter@gmail.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")

    # 5. Add default settings
    if not Setting.query.first():
        default_settings = [
            Setting(key='restaurant_name', value='RaysPOS&Restaurant'),
            Setting(key='vat_rate', value='15'),
            Setting(key='currency', value='$'),
            Setting(key='address', value='Kismayo, Somalia'),
            Setting(key='phone', value='+252 61 0000000')
        ]
        db.session.add_all(default_settings)
        db.session.commit()
        print("Default settings seeded!")

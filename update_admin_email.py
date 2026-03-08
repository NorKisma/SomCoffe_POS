from app import create_app
from app.extensions.db import db
from app.models.user import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.email = 'raystchcenter@gmail.com'
        db.session.commit()
        print("Admin email updated successfully to raystchcenter@gmail.com")
    else:
        print("Admin user not found. Please run seed_restaurant.py first.")

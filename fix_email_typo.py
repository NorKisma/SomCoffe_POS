from app import create_app
from app.extensions.db import db
from app.models.user import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        old_email = admin.email
        new_email = 'raystechcenter@gmail.com'
        admin.email = new_email
        db.session.commit()
        print(f"Updated admin email from {old_email} to {new_email}")
    else:
        print("Admin user not found.")

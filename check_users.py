from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("Listing all users in the system:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    if not users:
        print("No users found in the database.")

from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("### DEBUGGING USERS ###")
    for user in users:
        print(f"ID: {user.id} | USER: {repr(user.username)} | EMAIL: {repr(user.email)}")

from app import create_app, db
from app.models.user import User
from app.models.setting import Setting

app = create_app()
with app.app_context():
    # Ensure all tables are created (includes adding the pin column if not exists in some DBs, 
    # though usually adding column requires migration, for SQLite/MySQL 
    # db.create_all() works if the table doesn't exist. If it does, we might need a manual ALTER)
    try:
        db.create_all()
        print("Tables created/updated successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

    # Add default settings if they don't exist
    if not Setting.query.filter_by(key='auto_logout').first():
        Setting.set_val('auto_logout', 'OFF')
        print("Default auto_logout set to OFF")
    
    if not Setting.query.filter_by(key='session_timeout').first():
        Setting.set_val('session_timeout', '5')
        print("Default session_timeout set to 5")

    # Set a default PIN for the first admin if not set
    admin = User.query.filter_by(role='admin').first()
    if admin and not admin.pin:
        admin.pin = '1234'
        db.session.commit()
        print(f"Set default PIN 1234 for admin: {admin.username}")

from app import create_app
from app.models.setting import Setting

app = create_app()
with app.app_context():
    print(Setting.query.all())

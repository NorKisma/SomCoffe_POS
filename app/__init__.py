from flask import Flask
from config import Config
from app.extensions.db import db
from app.extensions.login_manager import login_manager
from app.extensions.mail import mail  # type: ignore
from flask_migrate import Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db)

    from app.models.user import User
    from app.models.category import Category
    from app.models.product import Product
    from app.models.table import Table
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.payment import Payment  # type: ignore
    from app.models.setting import Setting
    from app.models.employee import Employee

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_settings():
        from app.models.setting import Setting  # type: ignore
        return {
            'sys_name': Setting.get_val('restaurant_name', 'Rays POS'),
            'sys_address': Setting.get_val('address', 'Mogadishu, Somalia'),
            'sys_currency': Setting.get_val('currency', '$'),
            'Setting': Setting
        }

    # Register blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.dashboard.routes import dashboard_bp
    from app.blueprints.pos.routes import pos_bp
    from app.blueprints.products.routes import products_bp
    from app.blueprints.orders.routes import orders_bp
    from app.blueprints.reports import reports_bp
    from app.blueprints.users import users_bp
    from app.blueprints.settings import settings_bp
    from app.blueprints.employees import employees_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(pos_bp, url_prefix='/pos')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(employees_bp, url_prefix='/employees')

    return app

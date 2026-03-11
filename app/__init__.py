from flask import Flask, redirect, request as flask_request, flash, url_for, session
from config import Config
from .extensions import db, login_manager, mail, babel, migrate, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    def get_locale():
        # 1. User preference from session
        if 'language' in session:
            return session['language']
        # 2. Logged in user preference (if you add the column later)
        # if current_user.is_authenticated:
        #     return current_user.language
        # 3. Best match from browser
        return flask_request.accept_languages.best_match(app.config['LANGUAGES'])

    babel.init_app(app, locale_selector=get_locale)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from .models.user import User
    from .models.category import Category
    from .models.product import Product
    from .models.table import Table
    from .models.order import Order
    from .models.order_item import OrderItem
    from .models.payment import Payment
    from .models.setting import Setting
    from .models.employee import Employee
    from .models.customer import Customer
    from .models.expense import Expense

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_settings():
        try:
            return {
                'sys_name': Setting.get_val('restaurant_name', 'Rays POS'),
                'sys_address': Setting.get_val('address', 'Mogadishu, Somalia'),
                'sys_phone': Setting.get_val('phone', '+252 61XXXXXXX'),
                'sys_currency': Setting.get_val('currency', '$'),
                'Setting': Setting,
                'current_language': get_locale()
            }
        except Exception:
            return {
                'sys_name': 'Rays POS',
                'sys_address': 'Mogadishu, Somalia',
                'sys_phone': '+252 61XXXXXXX',
                'sys_currency': '$',
                'Setting': Setting,
                'current_language': 'so'
            }

    # CSRF error handler — redirect back with a user-friendly flash message
    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash('Waqtiga xiriirkaagu wuu dhacay. Dib u isku day. (Session expired — please try again)', 'warning')
        referrer = flask_request.referrer or url_for('auth.login')
        return redirect(referrer)

    # Register blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.pos import pos_bp
    from .blueprints.products import products_bp
    from .blueprints.orders import orders_bp
    from .blueprints.reports import reports_bp
    from .blueprints.users import users_bp
    from .blueprints.settings import settings_bp
    from .blueprints.employees import employees_bp
    from .blueprints.customers import customers_bp
    from .blueprints.kitchen import kitchen_bp
    from .blueprints.expenses import expenses_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(pos_bp, url_prefix='/pos')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(employees_bp, url_prefix='/employees')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(kitchen_bp, url_prefix='/kitchen')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')

    @app.route('/set_language/<lang>')
    def set_language(lang):
        if lang in app.config['LANGUAGES']:
            session['language'] = lang
            flash('Language changed successfully!', 'success')
        
        referrer = flask_request.referrer or url_for('dashboard.index')
        return redirect(referrer)

    return app

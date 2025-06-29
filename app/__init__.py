from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
mail = Mail()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-very-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'varmarahul2200@gmail.com'  # Use app-specific password
    app.config['MAIL_PASSWORD'] = 'cdva qkpn fihu mbpr'
    mail.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth_routes import auth
    from app.routes.user_routes import user
    from app.routes.provider_routes import provider
    from app.routes.admin_routes import admin

    from app.routes.home import home
    app.register_blueprint(home)

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(provider)
    app.register_blueprint(admin)

    with app.app_context():
        db.create_all()

    return app

from app.models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
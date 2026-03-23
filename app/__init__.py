from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.conversion import conversion_bp
    from app.routes.files import files_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(conversion_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app

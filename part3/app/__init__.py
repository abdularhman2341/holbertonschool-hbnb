from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()


def create_app(config_class=DevelopmentConfig):
    """Application factory for Flask app configuration."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    from app.api.v1.auth import auth_bp
    from app.api.v1.users import api as users_ns
    from flask_restx import Api

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API'
    )
    api.add_namespace(users_ns, path='/api/v1/users')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    return app

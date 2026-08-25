import os


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'default-super-secret-key'
    )
    JWT_SECRET_KEY = os.environ.get(
        'JWT_SECRET_KEY',
        'development-jwt-secret-key-change-me-32-bytes'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
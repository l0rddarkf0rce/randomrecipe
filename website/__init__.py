"""
Generate the app key to be used by the application to securely sign session cookies
"""
from flask import Flask
from .myFunctions import getSecretKey

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = getSecretKey()

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
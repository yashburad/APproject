from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError

class Auth:
    """Google Project Credentials"""
    CLIENT_ID = ('356186709623-6tb84gjrptp1ss0cificl90ia45qufa4.apps.googleusercontent.com')
    CLIENT_SECRET = 'gJ5hLx6ikRTAC8NlONLZ67Kx'
    REDIRECT_URI = 'https://localhost:5000/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager= LoginManager(app)
login_manager.login_view ='login'


from app import routes, models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from flask_mail import Mail

from whooshalchemy import IndexService

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text, DateTime, Float
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker



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

app.config.update(dict(
    MAIL_SERVER="smtp.googlemail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=1,
    MAIL_USERNAME="systems.quadcore@gmail.com",
    MAIL_PASSWORD="Quadcore00",
    ADMINS = ["systems.quadcore@gmail.com"]
))


mail = Mail(app)


engine = create_engine('sqlite:///app/searchdata.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class ProdSearch(Base):
   __tablename__ = 'prodSearch'
   __searchable__ = ['sprodname']  # these fields will be indexed by whoosh

   sproductId = Column(Integer, primary_key=True)
   sprodname = Column(Text)
   # sproddesp = Column(Text)
   # p_id = Column(Integer)

   def __repr__(self):
       return str(self.sproductId)
       # return '{0}(name={1})'.format(self.__class__.__name__, self.name)

Base.metadata.create_all(engine)

config = {"WHOOSH_BASE": "D:/YVJ/Documents/Ashoka University/Monsoon 2019/Advanced Programming - Anirban Mondal/MiniProject/git-sync/APproject/app/SearchProd/whoosh"}
index_service = IndexService(config=config, session=session)
index_service.register_class(ProdSearch)


def searchInProducts(s):
    return list(ProdSearch.search_query(s))

from app import routes, models

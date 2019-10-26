from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from whooshalchemy import IndexService
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text, DateTime
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from flask_mail import Mail


engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
session = Session()




app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
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



# Base = declarative_base()

from app import routes, models
# from app.models import products

class products(db.Model):
    __tablename__ = 'Products'
    __searchable__ = ['name']

    productId= Column(Integer, primary_key=True)
    name = Column(Text)
    # price= Column(Text)
    # product_img = Column(Text)
    # categoryId = Column(Integer)
    # brand  = Column(Text)
    # family  = Column(Text)
    # model  = Column(Text)
    # produced  = Column(Text)
    # materials  = Column(Text)
    # glass  = Column(Text)
    # diameter  = Column(Text)
    # height  = Column(Text)
    # wr  = Column(Text)
    # color  = Column(Text)
    # finish  = Column(Text)
    # type  = Column(Text)
    # display  = Column(Text)
    # chronograph  = Column(Text)
    # acoustic  = Column(Text)
    # additional  = Column(Text)
    # description  = Column(Text)
    # brand_img = Column(Text)

    # description=db.Column(db.String(120))
    # image2= db.Column(db.String())
    # image3= db.Column(db.String())

    # def __repr__(self):
    #    return '{0}(name={1})'.format(self.__class__.__name__, self.name)

    # def __repr__(self):
    #     return f"products('{self.name}', '{self.description}')"

    def __repr__(self):
       # return '{0}(id={1})'.format(self.__class__.__name__,self.id)
       return str(self.name)

# class Prodx(db.Model):
#     __tablename__ = 'prodx'
#     __searchable__ = ['name']
#
#     id = Column(Integer, primary_key=True)
#     name= Column(Text)
#
#     def __repr__(self):
#        # return '{0}(id={1})'.format(self.__class__.__name__,self.id)
#        return str(self.id)

db.Model.metadata.create_all(engine)

config = {"WHOOSH_BASE": "/tmp/whoosh"}
index_service = IndexService(config=config, session=db.session)
index_service.register_class(products)

#
# index_service = IndexService(config=app.config)
# index_service.register_class(products)

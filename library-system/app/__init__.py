from urllib.parse import quote

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from flask_migrate import Migrate
from flask_login import LoginManager
from .models import User
from .auth.routes import au
app = Flask(__name__)


db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'

app.secret_key = 'HGHJAHA^&^&*AJAVAHJ*^&^&*%&*^GAFGFAG'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/library_system_db?charset=utf8mb4" % quote("Admin@123")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from . import models
from . import index

login.init_app(app)

def load_user(user_id):
    return User.query.get(user_id)



# login = LoginManager(app)
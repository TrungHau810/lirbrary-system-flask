from urllib.parse import quote

import cloudinary
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)

# db = SQLAlchemy()
# login = LoginManager()
# login.login_view = 'auth.login'

app.secret_key = 'HGHJAHA^&^&*AJAVAHJ*^&^&*%&*^GAFGFAG'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/library_system_db?charset=utf8mb4" % quote("Admin@123")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# Initialize extensions BEFORE importing models
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

migrate = Migrate(app, db)
from . import models
from . import index



from . import admin

cloudinary.config(
    cloud_name="tthau2004",
    api_key="372274126191375",
    api_secret="Abk-RA6C6MUKDV34nOuFDhpLFjs",
    secure=True)


@login.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(user_id)
from urllib.parse import quote

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)


app.secret_key = 'HGHJAHA^&^&*AJAVAHJ*^&^&*%&*^GAFGFAG'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/library_db?charset=utf8mb4" % quote("Admin@123")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from . import models
from . import index
from . import admin
# login = LoginManager(app)
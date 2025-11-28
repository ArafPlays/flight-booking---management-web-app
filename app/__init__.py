from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app=Flask(__name__)

import os

# environment variable for session key. Also a default key for local users.
app.secret_key = os.environ.get("SECRET_KEY",'mjrajrjk294999$(@(@(.)))')

# environment variable for POSTGRES database url hosted on render. Also a default sqlite db for local users
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL","sqlite:///test.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes
#!/usr/bin/env python
# coding: utf-8

import pytz

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from whitenoise import WhiteNoise

from model import Base, User, Postit

# Flask
app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db/app.db?check_same_thread=False'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'blah blah blah'

# Database
db = SQLAlchemy(app, metadata=Base.metadata)
db.metadata.create_all(bind=db.engine)
db.init_app(app)

# Login
login_manager = LoginManager()
login_manager.init_app(app)

# Parameters
cfg = {
	'timezone': pytz.timezone('Europe/Paris'),
	'per_page': 5,
}
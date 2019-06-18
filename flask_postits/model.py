#!/usr/bin/env python
# coding: utf-8

import datetime
import os
import sys
import pytz

import sqlalchemy
import sqlalchemy.ext.declarative

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Boolean,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy import func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from werkzeug import generate_password_hash, check_password_hash

# use a naming convention for constraints
meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

# initialize ORM mapping
Base = sqlalchemy.ext.declarative.declarative_base(metadata=meta)

# model
class User(Base):
    __tablename__ = "users"

    def __init__(self, nick, password, name=None):
        self.user_nick = nick
        self.password = password

        if not name:
            self.user_name = nick
        else:
            self.user_name = name

    user_id = Column(Integer, primary_key=True)
    user_nick = Column(Text)
    user_name = Column(Text)
    user_pass = Column(Text)

    postits = relationship("Postit", back_populates="user")

    read_postits = association_proxy('read_by', 'user')

    @property
    def password(self):
        raise AttributeError

    @password.setter
    def password(self, password):
        self.user_pass = generate_password_hash(password)

    def check_pass(self, password):
        return check_password_hash(self.user_pass, password)

    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return "{}".format(self.user_name)


class Postit(Base):
    __tablename__ = "postits"

    def __init__(self, url, title, desc, image, content, user):
        self.postit_color = "#ffffa5"
        self.postit_url = url
        self.postit_title = title
        self.postit_desc = desc
        self.postit_image = image
        self.postit_content = content
        self.postit_date = datetime.datetime.now(pytz.utc)
        self.user = user

    postit_id = Column(Integer, primary_key=True)
    postit_color = Column(Text)
    postit_url = Column(Text)
    postit_title = Column(Text)
    postit_desc = Column(Text)
    postit_image = Column(Text)
    postit_content = Column(Text)
    postit_date = Column(DateTime(timezone=True))
    user_id = Column(Integer, ForeignKey(User.user_id))

    user = relationship("User", back_populates="postits")

    read_by = association_proxy('read_by', 'postit')

    @staticmethod
    def count(session):
        return session.query(func.count(Postit.postit_id)).scalar()

    def __repr__(self):
        return "<Postit(url = {}, title = {}, desc = {}, image = {}, content = {}, user = {})>".format(
            self.postit_url,
            self.postit_title,
            self.postit_desc,
            self.postit_image,
            self.postit_content,
            self.user,
        )

class ReadBy(Base):
    __tablename__ = 'read_by'

    postit_id = Column(Integer, ForeignKey(Postit.postit_id), primary_key=True)
    user_id = Column(Integer, ForeignKey(User.user_id), primary_key=True)

    postit = relationship('Postit', backref='read_by')
    user = relationship('User', backref='read_postits')

    def __repr__(self):
        return '<ReadBy(postit = {}, user = {})>'.format(self.postit, self.user)
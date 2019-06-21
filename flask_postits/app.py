#!/usr/bin/env python
# coding: utf-8

import flask
from flask import render_template, request

import flask_login
from flask_login import login_required, login_user, logout_user

from flask_paginate import Pagination, get_page_parameter

import sqlalchemy
from sqlalchemy import Table, Column, Integer, Numeric, Text, Time, DateTime, ForeignKey
from sqlalchemy import desc, and_
from sqlalchemy.orm.properties import ColumnProperty

from config import app, db, login_manager, cfg
from model import Base, User, Postit, ReadBy
from form import SignupForm, LoginForm, NewPostitForm

import datetime
import extraction
import requests
import timeago

# callbacks
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


def time_ago(date_ago):
    date_aware = date_ago.astimezone(cfg["timezone"])

    return timeago.format(
        date_aware, datetime.datetime.now(cfg["timezone"]), cfg["locale"]
    )

# routing
@app.route("/")
def index():
    page = flask.request.args.get(get_page_parameter(), type=int, default=1)

    if flask_login.current_user.is_authenticated:
        already_read = db.session.query(ReadBy.postit_id).filter(
            ReadBy.user == flask_login.current_user
        )
    else:
        already_read = db.session.query(ReadBy.postit_id).filter(sqlalchemy.sql.false())

    content = (
        db.session.query(Postit)
        .filter(Postit.postit_id.notin_(already_read))
        .order_by(desc(Postit.postit_date))
        .paginate(page=page, max_per_page=cfg["per_page"])
        .items
    )
    total = Postit.count(db.session)

    pagination = Pagination(
        css_framework="bootstrap4",
        page=page,
        total=total,
        type=int,
        default=1,
        per_page=cfg["per_page"],
        display_msg="post-its <strong>{start}</strong> à <strong>{end}</strong> — <strong>{total}</strong> post-its en tout",
    )

    return render_template(
        "index.html",
        title="Frigo | Accueil",
        postits=content,
        pagination=pagination,
        time_ago=time_ago
    )


@app.route("/bin")
@login_required
def bin():
    page = flask.request.args.get(get_page_parameter(), type=int, default=1)

    already_read = db.session.query(ReadBy.postit_id).filter(
        ReadBy.user == flask_login.current_user
    )

    content = (
        db.session.query(Postit)
        .filter(Postit.postit_id.in_(already_read))
        .order_by(desc(Postit.postit_date))
        .paginate(page=page, max_per_page=cfg["per_page"])
        .items
    )
    total = Postit.count(db.session)

    pagination = Pagination(
        css_framework="bootstrap4",
        page=page,
        total=total,
        type=int,
        default=1,
        per_page=cfg["per_page"],
        display_msg="post-its <strong>{start}</strong> à <strong>{end}</strong> — <strong>{total}</strong> post-its en tout",
    )

    return render_template(
        "bin.html", title="Frigo | Corbeille", postits=content, pagination=pagination
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if not flask_login.current_user.is_authenticated:
        form = SignupForm()
        if form.validate_on_submit():
            user = (
                db.session.query(User)
                .filter(User.user_nick.ilike(form.nickname.data))
                .first()
            )

            if not user:
                new_user = User(
                    form.nickname.data, form.mail.data, form.password.data, form.nickname.data
                )

                db.session.add(new_user)
                db.session.commit()

                return flask.redirect(flask.url_for("login"))

        return flask.render_template(
            "signup.html", title="Frigo | Inscription", form=form
        )

    return flask.redirect(flask.url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if not flask_login.current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            user = (
                db.session.query(User)
                .filter(User.user_nick.ilike(form.nickname.data))
                .first()
            )

            if user and user.check_pass(form.password.data):
                login_user(user)
                flask.flash("Connexion réussie.")
                next = flask.request.args.get("next")

                return flask.redirect(next or flask.url_for("index"))

        return render_template("login.html", title="Frigo | Connexion", form=form)

    return flask.redirect(flask.url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()

    return flask.redirect(flask.url_for("index"))


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = NewPostitForm()
    if form.validate_on_submit():
        try:
            html = requests.get(form.url.data).text
            extracted = extraction.Extractor().extract(html, source_url=form.url.data)

            postit = Postit(
                extracted.url,
                extracted.title,
                extracted.description,
                extracted.image,
                form.content.data,
                flask_login.current_user,
            )
            db.session.add(postit)
            db.session.commit()

            return flask.redirect(flask.url_for("index"))
        except ValueError:
            pass

    return render_template("new.html", title="Frigo | Nouveau post-it", form=form)


@app.route("/throw/<postit_id>")
@login_required
def throw(postit_id):
    postit = db.session.query(Postit).get(postit_id)

    already_read = (
        db.session.query(ReadBy)
        .filter(
            and_(ReadBy.postit_id == postit_id, ReadBy.user == flask_login.current_user)
        )
        .all()
    )

    if postit and not already_read:
        read_postit = ReadBy(postit=postit, user=flask_login.current_user)

        db.session.add(read_postit)
        db.session.commit()

    return flask.redirect(flask.url_for("index"))

if __name__ == "__main__":
    app.run()
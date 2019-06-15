#!/usr/bin/env python
# coding: utf-8

import flask
import flask_login
from flask import render_template, request
from flask_login import login_required, login_user, logout_user
from flask_paginate import Pagination, get_page_parameter

import sqlalchemy
from sqlalchemy import Table, Column, Integer, Numeric, Text, Time, DateTime, ForeignKey

from validator_collection import validators

from config import app, db, login_manager, cfg
from model import Base, User, Postit
from form import LoginForm, NewPostitForm

# callbacks
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

# routing
@app.route("/")
def index():
	page = flask.request.args.get(get_page_parameter(), type=int, default=1)

	content = db.session.query(Postit).paginate(page=page, max_per_page=cfg['per_page']).items
	total = Postit.count(db.session)

	pagination = Pagination(css_framework='bootstrap4', page=page, total=total, type=int, default=1, per_page=cfg['per_page'], display_msg='post-its <strong>{start}</strong> à <strong>{end}</strong> — <strong>{total}</strong> post-its en tout')

	return render_template('index.html', title='Frigo | Accueil', postits=content, pagination=pagination)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if not flask_login.current_user.is_authenticated:
		form = LoginForm()
		if form.validate_on_submit():
			user = (
				db.session.query(User)
				.filter(
					User.user_nick.ilike(form.nickname.data),
					)
				.first()
				)

			if user and user.check_pass(form.password.data):
				login_user(user)
				flask.flash('Connexion réussie.')
				next = flask.request.args.get('next')

				return flask.redirect(next or flask.url_for('index'))

		return render_template('login.html', title='Frigo | Connexion', form=form)

	return flask.redirect(flask.url_for('index'))

@app.route("/logout")
def logout():
	logout_user()
	
	return flask.redirect(flask.url_for('index'))

@app.route("/new", methods=['GET', 'POST'])
@login_required
def new():
	form = NewPostitForm()
	if form.validate_on_submit():
		try:
			postit = Postit(form.url.data, form.content.data)
			postit.user_id = flask_login.current_user.user_id
			db.session.add(postit)
			db.session.commit()

			return flask.redirect(flask.url_for('index'))
		except ValueError:
			pass

	return render_template('new.html', title='Frigo | Nouveau post-it', form=form)

@app.route("/delete/<id>")
@login_required
def delete(id):
	postit = db.session.query(Postit).get(id)

	if postit and postit.user == flask_login.current_user:
		db.session.delete(postit)
		db.session.commit()

	return flask.redirect(flask.url_for('index'))

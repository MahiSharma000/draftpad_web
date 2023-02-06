# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import *

from apps.authentication.util import verify_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            user.set_seen()
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500


# REST API code for Android App

@blueprint.route('/api/v1/login', methods=['POST'])
def api_login():
    username = request.form['username']
    password = request.form['password']
    # Locate user
    user = Users.query.filter_by(username=username).first()
    # Check the password
    if user and verify_pass(password, user.password):
        return jsonify({'status': 'OK', 'user': user.username, 'email': user.email, 'id': user.id})
    return jsonify({'status': 'ERROR', 'user': '', 'email': '', 'id': ''})

@blueprint.route('/api/v1/register', methods=['POST'])
def api_register():
    username = request.form['username']
    email = request.form['email']
    # Check usename exists
    user = Users.query.filter_by(username=username).first()
    if user:
        return jsonify({'status': 'ERROR', 'msg': 'Username already registered'})
    # Check email exists
    user = Users.query.filter_by(email=email).first()
    if user:
        return jsonify({'status': 'ERROR', 'msg': 'Email already registered'})
    # else we can create the user
    user = Users(**request.form)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': 'OK', 'msg': 'User created please login'})

@blueprint.route('/api/v1/logout', methods=['POST'])
def api_logout():
    return jsonify({'status': 'OK'})

@blueprint.route('/api/v1/user/<int:user_id>', methods=['GET'])
def api_user(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if user:    
        return jsonify({'status': 'OK', 'user': user.username, 'email': user.email, 'id': user.id})
    return jsonify({'status': 'ERROR', 'user': '', 'email': '', 'id': ''})

@blueprint.route('/api/v1/profile/<int:user_id>', methods=['GET'])
def api_profile(user_id):
    if current_user.is_authenticated:
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            return jsonify({'status': 'OK', 'profile': profile.to_json()})
        return jsonify({'status': 'ERROR', 'profile': ''})
    return jsonify({'status': 'ERROR', 'profile': ''})

@blueprint.route('/api/v1/profile/<int:user_id>', methods=['POST'])
def api_profile_update(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        profile.update(**request.form)
        db.session.commit()
        return jsonify({'status': 'OK', 'profile': profile.to_json()})
    return jsonify({'status': 'ERROR', 'profile': ''})



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
        return jsonify({'status': 'OK', 'username': user.username, 'email': user.email, 'id': user.id})
    return jsonify({'status': 'ERROR', 'username': '', 'email': '', 'id': ''})

@blueprint.route('/api/v1/register', methods=['POST'])
def api_register():
    print(request.form)
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']


    # Check usename exists
    user = Users.query.filter_by(username=username).first()
    if user:
        return jsonify({'status': 'ERROR', 'msg': 'Username already registered'})
    # Check email exists
    user = Users.query.filter_by(email=email).first()
    if user:
        return jsonify({'status': 'ERROR', 'msg': 'Email already registered'})
    # else we can create the user
    user = Users(username=username, email=email, password=password)
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
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        return jsonify({'status': 'OK', 'profile': profile.to_json()})
    return jsonify({'status': 'ERROR', 'profile': ''})

@blueprint.route('/api/v1/profile', methods=['POST'])
def api_profile_update():
    user_id = request.form['user_id']
    if user_id:
        profile = Profile.query.filter_by(user_id=user_id).first()
        user = Users.query.filter_by(id=user_id).first()
        if profile:
            profile.update(
                user_id=request.form['user_id'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                about=request.form['about'],
                profile_pic=request.form['profile_pic'],
                book_written = request.form['book_written'],
                followers = request.form['followers'],
                following = request.form['following'],
                is_premium = request.form['is_premium'],
                books_read = request.form['books_read'],
                dob = request.form['dob'],
                phone = request.form['phone']
            )
            db.session.commit()
            return jsonify({'status': 'OK'})
        else:
            profile = Profile(
                user_id=request.form['user_id'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                about=request.form['about'],
                profile_pic=request.form['profile_pic'],
                book_written = request.form['book_written'],
                followers = request.form['followers'],
                following = request.form['following'],
                is_premium = request.form['is_premium'],
                books_read = request.form['books_read'],
                dob = request.form['dob'],
                phone = request.form['phone']
                
            )
            db.session.add(profile)
            db.session.commit()
            return jsonify({'status': 'OK'})
    return jsonify({'status': 'ERROR'})

# all categories
@blueprint.route('/api/v1/categories', methods=['GET'])
def api_categories():
    categories = Category.query.all()
    if categories:
        return jsonify({'status': 'OK', 'categories': [category.to_json() for category in categories]})
    return jsonify({'status': 'ERROR', 'categories': ''})



@blueprint.route('/api/v1/category/<int:category_id>', methods=['GET'])
def api_category(category_id):
    #get books by category id
    books = Book.query.filter_by(category_id=category_id).all()
    if books:
        book_data = []
        for book in books:
            user = Users.query.filter_by(id=book.user_id).first()
            chapter_count = Chapter.query.filter_by(book_id=book.id).count() 
            book_data.append({
                'id': book.id,
                'cover': book.cover,
                'title': book.title,
                'user_id': book.user_id,
                'username': user.username,
                'category_id': book.category_id,
                'description': book.description,
                'created_at': book.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': book.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'lang': book.lang,
                'views': book.views,
                'chapters': chapter_count
            })
        return jsonify({'status': 'OK', 'books': book_data})
    return jsonify({'status': 'OK', 'books': []})    


@blueprint.route('/api/v1/category', methods=['POST'])
def api_category_add():
    category = Category(**request.form)
    db.session.add(category)
    db.session.commit()
    return jsonify({'status': 'success'})


@blueprint.route('/api/v1/book', methods=['POST'])
def api_book_add():
    book = Book(**request.form)
    db.session.add(book)
    db.session.commit()
    return jsonify({'status': 'success', 'msg': 'Book added'})

@blueprint.route('/api/v1/book/<int:book_id>', methods=['GET'])
def api_book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book:
       
        user = Users.query.filter_by(id=book.user_id).first()
        chapter_count = Chapter.query.filter_by(book_id=book.id).count() 
        book_data= ({
            'id': book.id,
            'cover': book.cover,
            'title': book.title,
            'user_id': book.user_id,
            'username': user.username,
            'category_id': book.category_id,
            'description': book.description,
            'created_at': book.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': book.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'lang': book.lang,
            'views': book.views,
            'chapters': chapter_count
        })
        return jsonify({'status': 'OK', 'book': book_data})
    return jsonify({'status': 'ERROR', 'book': ''})

#get comments by chapter id
@blueprint.route('/api/v1/comments/<int:chapter_id>', methods=['GET'])
def api_comments(chapter_id):
    comments = Comment.query.filter_by(chapter_id=chapter_id).all()
    if comments:
        comment_data= []
        for comment in comments:
            user = Users.query.filter_by(id=comment.user_id).first()
            comment_data.append({
                'id': comment.id,
                'user_id': comment.user_id,
                'username': user.username,
                'chapter_id': comment.chapter_id,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({'status': 'OK', 'comments': comment_data})
    return jsonify({'status': 'ERROR', 'comments': []})

#post comment by chapter id
@blueprint.route('/api/v1/comment', methods=['POST'])
def api_comment_add():
    comment = Comment(**request.form)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'status': 'success', 'msg': 'Comment added'})


@blueprint.route('/api/v1/chapters/<int:book_id>', methods=['GET'])
def api_chapters(book_id):
    chapters = Chapter.query.filter_by(book_id=book_id).all()
    if chapters:
        
        chapter_data = []
        for chapter in chapters:
            book = Book.query.filter_by(id=chapter.book_id).first()
            chapter_data.append({
                'id': chapter.id,
                'title': chapter.title,
                'content': chapter.content,
                'book_id': chapter.book_id,
                'book_title': book.title,
                'book_views': book.views,
                'category_id': chapter.category_id,
                'user_id' : chapter.user_id,
                'created_at': chapter.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': chapter.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status' : chapter.status,
                'total_likes' : chapter.total_likes,
                'total_comments' : chapter.total_comments,
            })
        return jsonify({'status': 'OK', 'chapters': chapter_data})
    return jsonify({'status': 'ERROR', 'chapters': []})

#get a chapter by chapter id
@blueprint.route('/api/v1/chapter/<int:chapter_id>', methods=['GET'])
def api_chapter(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    if chapter:
        book = Book.query.filter_by(id=chapter.book_id).first()
        chapter_data=({
            'id': chapter.id,
            'title': chapter.title,
            'content': chapter.content,
            'book_id': chapter.book_id,
            'book_title': book.title,
            'book_views': book.views,
            'category_id': chapter.category_id,
            'user_id' : chapter.user_id,
            'created_at': chapter.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': chapter.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status' : chapter.status,
            'total_likes' : chapter.total_likes,
            'total_comments' : chapter.total_comments,
            })
        return jsonify({'status': 'OK', 'chapter': chapter_data})
    return jsonify({'status': 'ERROR', 'chapter': ''})

@blueprint.route('api/v1/chapter', methods=['POST'])
def api_chapter_add():
    chapter = Chapter(**request.form)
    db.session.add(chapter)
    db.session.commit()
    return jsonify({'status': 'success', 'msg': 'Chapter added'})


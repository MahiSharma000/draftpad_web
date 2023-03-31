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

import stripe
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
        user = Users.query.filter_by(id=profile.user_id).first()
        
        profile_data= ({
            'user_id': profile.user_id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'about': profile.about,
            'profile_pic': profile.profile_pic,
            'book_written': profile.book_written,
            'followers': profile.followers,
            'following': profile.following,
            'username': user.username,
            'is_premium': profile.is_premium,
            'book_read': profile.book_read,
            'dob': profile.dob,
            'phone': profile.phone
        })
        return jsonify({'status': 'OK', 'profile': profile_data})
    return jsonify({'status': 'ERROR', 'profile': ''})

def covert_str_to_date(date_str):
    return datetime .strptime(date_str, '%d-%m-%Y')

@blueprint.route('/api/v1/profile', methods=['POST'])
def api_profile_update():
    user_id = request.form['user_id']
    if user_id:
        profile = Profile.query.filter_by(user_id=user_id).first()
        user = Users.query.filter_by(id=user_id).first()
        dob = covert_str_to_date(request.form['dob'])
        print('dob', dob)
        if profile:
            profile.first_name = request.form['first_name']
            profile.last_name = request.form['last_name']
            profile.about = request.form['about']
            profile.profile_pic = request.form['profile_pic']
            profile.book_written = request.form['book_written']
            profile.followers = request.form['followers']
            profile.following = request.form['following']
            profile.is_premium = True if request.form['is_premium'] == 'true' else False
            profile.books_read = request.form['books_read']
            profile.dob = dob
            profile.phone = request.form['phone']
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
                is_premium = True if request.form['is_premium'] == 'true' else False,
                books_read = request.form['books_read'],
                dob = dob,
                phone = request.form['phone']
                
            )
            db.session.add(profile)
            db.session.commit()
            return jsonify({'status': 'OK'})
    return jsonify({'status': 'ERROR'})

@blueprint.route('/api/v1/book', methods=['POST'])
def api_book_add():
    book = Book.query.filter_by(id = request.form['id']).first()
    if book:
        book.title = request.form['title']
        book.user_id = request.form['user_id']
        book.cover = request.form['cover']
        book.status = request.form['status']
        book.description = request.form['description']
        book.category_id = request.form['category_id']
        book.status=request.form['status']
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Book updated', 'id': book.id})
    else:
        book = Book(
            title=request.form['title'],
            user_id = request.form['user_id'],
            cover=request.form['cover'],
            description=request.form['description'],
            category_id=request.form['category_id'],
        )
        db.session.add(book)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Book added', 'id': book.id})
    

@blueprint.route('api/v1/chapter', methods=['POST'])
def api_chapter_update():
    book_id = request.form['book_id']
    if book_id:
        #get chapter by id 
        chapter = Chapter.query.filter_by(id=request.form['id']).first()
        if chapter:
            chapter.title = request.form['title']
            chapter.content = request.form['content']
            chapter.book_id = request.form['book_id']
            chapter.category_id = request.form['category_id']
            chapter.user_id = request.form['user_id']
            chapter.status = request.form['status']
            chapter.total_comments = request.form['total_comments']
            chapter.total_likes = request.form['total_likes']
            
            db.session.commit()
            return jsonify({'status': 'OK'})
        else:
            chapter = Chapter(
                title=request.form['title'],
                content=request.form['content'],
                book_id=request.form['book_id'],
                user_id=request.form['user_id'],
                status=request.form['status'],
                total_comments=request.form['total_comments'],
                total_likes=request.form['total_likes'],
                category_id=request.form['category_id']
            )
            db.session.add(chapter)
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


@blueprint.route('/api/v1/get_profile/<int:user_id>', methods=['GET'])
def api_author_profile(user_id):
    #get profile by user id
    profile = Profile.query.filter_by(user_id=user_id).all()
    if profile:
        profile_data = []
        for profile in profile:
            user = Users.query.filter_by(id=profile.user_id).first()
            profile_data.append({
                'id': profile.id,
                'user_id': profile.user_id,
                'username': user.username,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'about': profile.about,
                'profile_pic': profile.profile_pic,
                'book_written': profile.book_written,
                'followers': profile.followers,
                'following': profile.following,
                'is_premium': profile.is_premium,
                'books_read': profile.books_read,
                'dob': profile.dob,
                'phone': profile.phone,
                'created_at': profile.created_at,
                'updated_at': profile.updated_at,

            })
        print(profile_data)
        return jsonify({'status': 'OK', 'author': profile_data[0]})
    return jsonify({'status': 'ERROR', 'author': ''})



@blueprint.route('/api/v1/category/<int:category_id>', methods=['GET'])
def api_category(category_id):
    books = Book.query.filter_by(category_id=category_id).filter_by(status=1).all()
    if books:
        book_data = []
        for book in books:
            user = Users.query.filter_by(id=book.user_id).first()
            chapter_count = Chapter.query.filter_by(book_id=book.id).count() 
            book_data.append({
                'status' :book.status,
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
            'status' :book.status,
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
            profile = Profile.query.filter_by(user_id=user.id).first()
            comment_data.append({
                'id': comment.id,
                'user_id': comment.user_id,
                'username': user.username,
                'chapter_id': comment.chapter_id,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'profile_pic': profile.profile_pic,
            })
        comment_data.sort(key=lambda x: x['id'], reverse=True)
        return jsonify({'status': 'OK', 'comments': comment_data})
    return jsonify({'status': 'ERROR', 'comments': []})

#post comment by chapter id
@blueprint.route('/api/v1/comment', methods=['POST'])
def api_comment_add():
    try:
        profile = Profile.query.filter_by(user_id=request.form.get('user_id')).first()
        comment = Comment(
        content = request.form.get('content'),
        user_id = request.form.get('user_id'),
        chapter_id = request.form.get('chapter_id'),
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Comment added'})
    except:
        return jsonify({'status': 'error', 'msg': 'Comment not added'})


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



@blueprint.route('/api/v1/follower', methods=['POST'])
def api_follower_add():
    try:
        follower = Follower(
        user_id = request.form.get('user_id'),
        follower_id = request.form.get('follower_id'),
        )
        db.session.add(follower)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Follower added'})
    except:
        return jsonify({'status': 'error', 'msg': 'Follower not added'})
    
@blueprint.route('/api/v1/download', methods=['POST'])
def api_download_add():
    try:
        download = Download(
        user_id = request.form.get('user_id'),
        book_id = request.form.get('book_id'),
        )
        db.session.add(download)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': ' Book Download '})
    except:
        return jsonify({'status': 'error', 'msg': 'Book not Download'})

#get books by user_id and status
@blueprint.route('/api/v1/books/<int:user_id>/<string:status>', methods=['GET'])
def api_books(user_id, status):
    books = Book.query.filter_by(user_id=user_id).filter_by(status=status).all()
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
                'status' :book.status,
                'category_id': book.category_id,
                'description': book.description,
                'created_at': book.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': book.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'lang': book.lang,
                'views': book.views,
                'chapters': chapter_count
            })
        return jsonify({'status': 'OK', 'books': book_data})
    return jsonify({'status': 'ERROR', 'books': []})

#get profiles by name
@blueprint.route('/api/v1/get_profiles/<string:name>', methods=['GET'])
def api_get_profiles(name):
    profiles = Profile.query.filter(Profile.first_name.like(name+'%')).all()
    if profiles:
        profile_data = []
        
        for profile in profiles:
            user = Users.query.filter_by(id=profile.user_id).first()
            if user is not None:
                profile_data.append({
                    'id': profile.id,
                    'user_id': profile.user_id,
                    'username': user.username,
                    'first_name': profile.first_name,
                    'last_name': profile.last_name,
                    'about': profile.about,
                    'profile_pic': profile.profile_pic,
                    'book_written': profile.book_written,
                    'followers': profile.followers,
                    'following': profile.following,
                    'is_premium': profile.is_premium,
                    'books_read': profile.books_read,
                    'dob': profile.dob,
                    'phone': profile.phone,
                    'created_at': profile.created_at,
                    'updated_at': profile.updated_at,
                })
        return jsonify({'status': 'OK', 'profiles': profile_data})
    return jsonify({'status': 'ERROR', 'profiles': []})

#get books by name
@blueprint.route('/api/v1/get_books/<string:name>', methods=['GET'])
def api_get_books(name):
    books = Book.query.filter(Book.title.like('%'+name+'%')).all()
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
                'status' :book.status,
                'category_id': book.category_id,
                'description': book.description,
                'created_at': book.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': book.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'lang': book.lang,
                'views': book.views,
                'chapters': chapter_count
            })
        return jsonify({'status': 'OK', 'books': book_data})
    return jsonify({'status': 'ERROR', 'books': []})

#get reading list by name
@blueprint.route('/api/v1/get_reading_list/<string:name>', methods=['GET'])
def api_get_reading_list(name):
    reading_list = ReadingList.query.filter(ReadingList.title.like('%'+name+'%')).all()
    if reading_list:
        reading_list_data = []
        for reading in reading_list:
            user = Users.query.filter_by(id=reading.user_id).first()
            reading_list_data.append({
                'id': reading.id,
                'title': reading.title,
                'user_id': reading.user_id,
                'username': user.username,
                'book_id': reading.book_id,
                'chapter_id': reading.chapter_id,
                'created_at': reading.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': reading.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        return jsonify({'status': 'OK', 'reading_list': reading_list_data})
    return jsonify({'status': 'ERROR', 'reading_list': []})


# add a stripe payment endpoint
@blueprint.route('/api/v1/create-checkout-session', methods=['POST'])
def create_checkout_session():
    stripe.api_key = 'sk_test_51MqsCESCz8rZMjh8Kwew9NTEiBpxHqEQ9xaqITnSYty7NIsPT831jc46picJ7vjMrqjD0cjy9IPqJikqOVi6i46e00Ko8jRijT'

    # Use an existing Customer ID if this is a returning customer
    customer = stripe.Customer.create()
    ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2022-11-15',
    )
    paymentIntent = stripe.PaymentIntent.create(
        amount=1,
        currency='inr',
        customer=customer['id'],
        automatic_payment_methods={
        'enabled': True,
        },
    )
    return jsonify(paymentIntent=paymentIntent.client_secret,
                    ephemeralKey=ephemeralKey.secret,
                    customer=customer.id,
                    publishableKey='pk_test_51MqsCESCz8rZMjh8kM2ElCXyKd8L4HIE3zhVAASQELg8ZLwVYpserzPdxOt5YHAy4FBp33TBH5rMgGKX42m0mcQE004Buf8yVW')

#change password 
@blueprint.route('/api/v1/change_password', methods=['POST'])
def api_change_password():
    user_id = request.form.get('user_id')
    data = request.get_json()
    user = Users.query.filter_by(id=user_id).first()
    old_password = request.form.get('old_password')
    if user is not None:
        if (old_password==user.password):
            user.password = request.form.get('new_password')
            db.session.commit()
            return jsonify({'status': 'OK', 'message': 'Password changed successfully'})
        return jsonify({'status': 'ERROR', 'message': 'Old password is incorrect'})
    return jsonify({'status': 'ERROR', 'message': 'User not found'})

#get books with max views whose status is published
@blueprint.route('/api/v1/get_books_max_views', methods=['GET'])
def api_get_books_with_max_views():
    books = Book.query.filter_by(status=1).limit(10).all()
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
                'status' :book.status,
                'category_id': book.category_id,
                'description': book.description,
                'created_at': book.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': book.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'lang': book.lang,
                'views': book.views,
                'chapters': chapter_count
            })
            book_data.sort(key=lambda x: x['views'], reverse=True)
        return jsonify({'status': 'OK', 'books': book_data})
    return jsonify({'status': 'ERROR', 'books': []})

#post report
@blueprint.route('/api/v1/report', methods=['POST'])
def api_report():
    report = Report(
        user_id=request.form.get('user_id'),
        book_id=request.form.get('book_id'),
        report_type=request.form.get('report_type'),
        report_reason=request.form.get('report_reason'),
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'status': 'OK', 'message': 'Reported successfully'})

 #update  number of comments in chapter table 
@blueprint.route('/api/v1/update_comment', methods=['POST'])
def api_update_comment():
    chapter_id = request.form['id']
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    if chapter is not None:
        chapter.total_comments = chapter.total_comments + 1
        db.session.commit()
        return jsonify({'status': 'OK'})
    return jsonify({'status': 'ERROR'})

#check the user has liked the chapter
@blueprint.route('/api/v1/check_like', methods=['POST'])
def api_check_like():
    chapter_id = request.form['chapter_id']
    user_id = request.form['user_id']
    like = LikedChapter.query.filter_by(chapter_id=chapter_id).filter_by(user_id=user_id).first()
    if like is not None:
        db.session.commit()
        return jsonify({'status': 'OK'})
    
    return jsonify({'status': 'ERROR'})

#add likes to chapter
@blueprint.route('/api/v1/add_like', methods=['POST'])
def api_add_like():
    chapter_id = request.form['chapter_id']
    user_id = request.form['user_id']
    like = LikedChapter(
        chapter_id=chapter_id,
        user_id=user_id,
    )
    db.session.add(like)
    db.session.commit()
    return jsonify({'status': 'OK'})

#delete like from chapter
@blueprint.route('/api/v1/delete_like', methods=['POST'])
def api_delete_like():
    chapter_id = request.form['chapter_id']
    user_id = request.form['user_id']
    like = LikedChapter.query.filter_by(chapter_id=chapter_id).filter_by(user_id=user_id).first()
    if like is not None:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'status': 'OK'})
    return jsonify({'status': 'ERROR'})

#update status of book by id
@blueprint.route('/api/v1/update_status', methods=['POST'])
def api_update_status():
    book_id = request.form['id']
    book = Book.query.filter_by(id=book_id).first()
    if book is not None:
        book.status = 1
        db.session.commit()
        return jsonify({'status': 'OK'})
    return jsonify({'status': 'ERROR'})

#get category by id
@blueprint.route('/api/v1/get_category/<int:category_id>', methods=['GET'])
def api_get_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category is not None:
        return jsonify({'status': 'OK', 'category': category.name})
    return jsonify({'status': 'ERROR', 'category': ''})

#post reading list
@blueprint.route('/api/v1/reading_list', methods=['POST'])
def api_reading_list():
    reading_list = ReadingList(
        name="NULL",
        user_id=request.form.get('user_id'),
        book_id=request.form.get('book_id'),
    )
    db.session.add(reading_list)
    db.session.commit()
    return jsonify({'status': 'OK', 'message': 'Added to reading list successfully'})
#update number of views in book table
@blueprint.route('/api/v1/update_views', methods=['POST'])
def api_update_views():
    book_id = request.form['id']
    book = Book.query.filter_by(id=book_id).first()
    if book is not None:
        book.views = book.views + 1
        db.session.commit()
        return jsonify({'status': 'OK'})
    return jsonify({'status': 'ERROR'})

#get followers of user
@blueprint.route('/api/v1/get_followers/<int:user_id>', methods=['GET'])
def api_get_followers(user_id):
    followers = Follower.query.filter_by(user_id=user_id).all()
    if followers:
        follower_data = []
        for follower in followers:
            profile = Profile.query.filter_by(user_id=follower.follower_id).first()
            user = Users.query.filter_by(id=follower.follower_id).first()
            follower_data.append({
                'id': user.id,
                'username': user.username,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'about': profile.about,
                'profile_pic': profile.profile_pic,
                'book_written': profile.book_written,
                'followers': profile.followers,
                'following': profile.following,
                'is_premium': profile.is_premium,
                'books_read': profile.books_read,
                'dob': profile.dob,
                'phone': profile.phone,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                
            })
        return jsonify({'status': 'OK', 'followers': follower_data})
    return jsonify({'status': 'ERROR', 'followers': []})

#add book in reading list
@blueprint.route('/api/v1/add_reading_later', methods=['POST'])
def api_add_reading_later():
    book_id = request.form['book_id']
    user_id = request.form['user_id']
    reading_list = ReadingList(
        book_id=book_id,
        user_id=user_id,
    )
    db.session.add(reading_list)
    db.session.commit()
    return jsonify({'status': 'OK'})


           
                          

                          


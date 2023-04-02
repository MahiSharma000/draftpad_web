# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.authentication.models import *


@blueprint.route('/index')
@login_required
def index():
    return redirect('/admin/dashboard')


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


@blueprint.route('/admin/dashboard')
def admin_dashboard():
    
    users = Users.query.all()    
    books = Book.query.all() 
    categories = Category.query.all()
    Comments = Comment.query.all()
    Reports = Report.query.all()
    return render_template('admin/dashboard.html', users=users, books=books, categories=categories,Comments=Comments,Reports=Reports)
    
@blueprint.route('/admin/users')
def admin_users():
    users = Users.query.all()
    return render_template('home/userDetails.html', users=users)

@blueprint.route('/admin/user/<int:id>')
def userDetails(id):
    user = Users.query.get(id)
    readingList=ReadingList.query.filter_by(user_id=id).all()
    comments=Comment.query.filter_by(user_id=id).all()
    reports=Report.query.filter_by(user_id=id).all()
    books=Book.query.filter_by(user_id=id).all()
    profile=Profile.query.filter_by(user_id=id).first()
    subscriptions=Subscriptions.query.filter_by(user_id=id).all()
    followers=Follower.query.filter_by(user_id=id).all()
    return render_template('home/user.html', user=user,readingList=readingList,comments=comments,reports=reports,books=books,profile=profile,subscriptions=subscriptions,followers=followers)
    

@blueprint.route('/user/<int:id>/action/delete')
def userDelete(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/admin/users')

#edit user
@blueprint.route('/user/<int:id>/action/edit', methods=['GET', 'POST'])
def userEdit(id):
    user = Users.query.get(id)
    if request.method == 'POST':
        user.email = request.form['email']
        user.username = request.form['username']
        user.password = request.form['password']
        db.session.commit()
        return redirect('/admin/users')
    return render_template('home/editProfile.html', user=user)


@blueprint.route('/book/<int:id>/action/delete')
def bookDelete(id):
    book=Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return redirect('/admin/books')

@blueprint.route('/admin/categories')
def admin_categories():
    categories = Category.query.all()
    return render_template('home/categories.html', categories=categories)

#add categories
@blueprint.route('/admin/category/<int:id>')
def categories(id):    
    category = Category.query.get(id)
    return render_template('home/categories_id.html', category=category)

@blueprint.route('/category/<int:id>/action/delete')
def categoryDelete(id):
    category = Category.query.get(id)
    db.session.delete(category)
    db.session.commit()
    return redirect('/admin/categories')

@blueprint.route('/admin/books')
def admin_books():
    books = Book.query.all()
    return render_template('home/bookDetails.html', books=books)


@blueprint.route('/admin/book/<int:id>')
def bookDetails(id):
    book = Book.query.get(id)
    return render_template('home/bookDetails_id.html', book=book)

@blueprint.route('/admin/comments')
def admin_comments():
    comments = Comment.query.order_by(Comment.id.desc()).all()
    # get chapter details for each comment
    for comment in comments:
        chapter = Chapter.query.get(comment.chapter_id)
        user = Users.query.get(comment.user_id)
        comment.chapter = chapter
        comment.user = user
    return render_template('home/comments.html', comments=comments)

@blueprint.route('/admin/comment/<int:id>')
def commentDetails(id):
    comment = Comment.query.get(id)
    return render_template('home/comments_id.html', comment=comment)

@blueprint.route('/comment/<int:id>/action/delete')
def commentDelete(id):
    comment = Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    return redirect('/admin/comments')

@blueprint.route('/admin/reports')
def admin_reports():
    reports = Report.query.all()
    return render_template('home/report.html', reports=reports)

@blueprint.route('/report/<int:id>/action/delete')
def reportDelete(id):
    report = Report.query.get(id)
    db.session.delete(report)
    db.session.commit()
    return redirect('/admin/reports')

@blueprint.route('/admin/report/<int:id>')
def reportDetails(id):
    report = Report.query.get(id)
    return render_template('home/report_id.html', report=report)

@blueprint.route('/admin/member/add', methods=['GET', 'POST'])
def addMember():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        user = Users(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/admin/users')

    return render_template('home/add_new_member.html')










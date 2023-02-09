# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, redirect
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
    
@blueprint.route('/home/userDetails')
def admin_userDetails():
    users = Users.query.all()
    return render_template('admin/userDetails.html', users=users)








from email.mime import image
from flask_login import UserMixin
from apps import db, login_manager

from apps.authentication.util import hash_pass
from datetime import datetime, timedelta



class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    last_seen = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def set_seen(self):
        self.last_seen = db.func.current_timestamp()
        db.session.commit()

    def get_last_seen(self):
        # show the last seen time in a human readable format
        return self.last_seen.strftime('%Y-%m-%d %H:%M:%S')

    def __repr__(self):
        return str(self.username)

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None

class Profile(db.Model):
    __tablename__ = 'Profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    about = db.Column(db.String(64))
    profile_pic = db.Column(db.String(64))
    book_written = db.Column(db.Integer, default=0)
    followers = db.Column(db.Integer, default=0)
    following = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    is_premium = db.Column(db.Boolean, default=False)
    books_read = db.Column(db.Integer, default=0)
    dob = db.Column(db.DateTime)
    phone = db.Column(db.String(64))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def make_premium(self):
        self.is_premium = True
        self.update()
    
    def inc_book_written(self):
        self.book_written += 1
        self.update()

    def inc_followers(self):
        self.followers += 1
        self.update()
    
    def inc_following(self):
        self.following += 1
        self.update()

    def inc_books_read(self):
        self.books_read += 1
        self.update()

    def dec_books_read(self):
        self.books_read -= 1
        self.update()
    
    def dec_followers(self):
        self.followers -= 1
        self.update()
    
    def dec_following(self):
        self.following -= 1
        self.update()
    
    def dec_book_written(self):
        self.book_written -= 1
        self.update()
    
    def __repr__(self):
        return str(self.first_name)

class Category(db.Model):

    __tablename__ = 'Categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return str(self.name)
    
    def to_json(self):
        return {
            'id' : self.id,
            'name' : self.name
        }

class Book(db.Model):
    status_info = {
        'draft' : 0,
        'published' : 1,
        'blocked' : 2
    }
    __tablename__ = 'Books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    category_id = db.Column(db.Integer, db.ForeignKey('Categories.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    cover = db.Column(db.String(64))
    status = db.Column(db.Integer, default=0)
    description = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    views = db.Column(db.Integer, default=0)
    lang = db.Column(db.String(64), default='en')
    

    def save(self):
        db.session.add(self)
        db.session.commit()
        print('Book saved')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        print('Book deleted')

    def __repr__(self):
        return str(self.title)

    def inc_views(self):
        self.views += 1
        db.session.commit()

    def update_status(self, status_value):
        self.status = self.status_info[status_value]
        db.session.commit()

    def to_json(self):
        return {
            'id' : self.id,
            'title' : self.title,
            'category_id' : self.category_id,
            'user_id' : self.user_id,
            'cover' : self.cover,
            'status' : self.status,
            'description' : self.description,
            'created_at' : self.created_at,
            'updated_at' : self.updated_at,
            'views' : self.views,
            'lang' : self.lang
        }

class Chapter(db.Model):

    status_info = {
        'draft' : 0,
        'published' : 1,
        'blocked' : 2
    }

    __tablename__ = 'Chapter'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    content = db.Column(db.String(64))
    book_id = db.Column(db.Integer, db.ForeignKey('Books.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('Categories.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    status = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    total_likes = db.Column(db.Integer, default=0)

    def save(self):
        db.session.add(self)
        db.session.commit()
        print('Story saved')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        print('Story deleted')

    def update(self):
        db.session.commit()
        print('Story updated')

    def inc_likes(self):
        self.total_likes += 1
        db.session.commit()

    def dec_likes(self):
        self.total_likes -= 1
        db.session.commit()

    def inc_comment_count(self):
        self.total_comments += 1
        db.session.commit()
    
    def dec_comment_count(self):
        self.total_comments -= 1
        db.session.commit()

    def update_status(self, status_value):
        self.status = self.status_info[status_value]
        db.session.commit()

    def __repr__(self):
        return str(self.title)

class Comment(db.Model):
    __tablename__ = 'Comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(64))
    chapter_id = db.Column(db.Integer, db.ForeignKey('Chapter.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()
        print('Comment saved')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        print('Comment deleted')

    def update(self):
        db.session.commit()
        print('Comment updated')

    def __repr__(self):
        return str(self.content)

class Download(db.Model):
    __tablename__ = 'Downloads'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('Books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()
        print('Download saved')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        print('Download deleted')

    def update(self):
        db.session.commit()
        print('Download updated')

    def __repr__(self):
        return str(self.book_id)

class Subscriptions(db.Model):
    __tablename__ = 'Subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    amount = db.Column(db.Integer, default=200)
    duration = db.Column(db.Integer, default=30)
    transaction_id = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()
        print('Subscription saved')

    def is_expired(self):
        if self.updated_at + timedelta(days=self.duration) < datetime.now():
            return True
        return False

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        print('Subscription deleted')

    def update(self):
        db.session.commit()
        print('Subscription updated')

    def __repr__(self):
        return str(self.user_id)

class ReadingList(db.Model):
    __tablename__ = 'ReadingList'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('Books.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()
        print('ReadingList saved')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        print('ReadingList deleted')

    def update(self):
        db.session.commit()
        print('ReadingList updated')

    def __repr__(self):
        return str(self.user_id)

class Follower(db.Model):
    __tablename__ = 'Followers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    follower_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()
        print('Follower saved')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        print('Follower deleted')

    def update(self):
        db.session.commit()
        print('Follower updated')

    def get_followers(self,user_id):
        return Follower.query.filter_by(user_id=user_id).all()
    
    def get_following(self,user_id):
        return Follower.query.filter_by(follower_id=user_id).all()
        
    def __repr__(self):
        return str(self.user_id)


class Report(db.Model):
    __tablename__ = 'Reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('Books.id'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('Chapter.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('Comments.id'))
    report_type = db.Column(db.String(64))
    report_reason = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    #def save(self):
     # db.session.add(self)image.png
      #  db.session.commit()
       # print('Report saved')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        print('Report deleted')

    def update(self):
        db.session.commit()
        print('Report updated')

    def __repr__(self):
        return str(self.user_id)



from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    user_hot = db.relationship('HotTopic', backref='author', lazy='dynamic')
    user_journal = db.relationship('Journal', backref='author', lazy='dynamic')
    user_Categories = db.relationship('Categories', backref='author', lazy='dynamic')
    user_dyk = db.relationship('Did_you_know', backref='author', lazy='dynamic')
    user_op = db.relationship('Other_projects', backref='author', lazy='dynamic')


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    post_comment = db.relationship('Comment', backref="post", lazy=True)

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    comment_username = db.Column(db.String(64), db.ForeignKey('user.username'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment = db.Column(db.String(140))

    def __repr__(self):
        return '<Comment {}>'.format(self.comment)


class HotTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_name = db.Column(db.String)
    title = db.Column(db.String(64))
    description = db.Column(db.String(64))
    exlink = db.Column(db.Integer)

    def __repr__(self):
        return '<HotTopic {}>'.format(self.title)


class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(64))
    issue = db.Column(db.String(64))

    def __repr__(self):
        return '<Journal {}>'.format(self.title)


class Did_you_know (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(140))
    content = db.Column(db.String(200))

    def __repr__(self):
        return '<Did_you_know {}>'.format(self.topic)

class Other_projects (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Pname = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(200))

    def __repr__(self):
        return '<Other_projects {}>'.format(self.Pname)

class Categories (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(200))

    def __repr__(self):
        return '<Categories {}>'.format(self.category)


class Contact_Us(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact_username = db.Column(db.String(64), db.ForeignKey('user.username'))
    title = db.Column(db.String(64))
    details = db.Column(db.String(64))
    def __repr__(self):
        return '<ContactUs {}>'.format(self.title)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(150))
    details = db.Column(db.String(500))
    date = db.Column(db.String(64))
    url = db.Column(db.String(200))
    def __repr__(self):
        return '<News {}>'.format(self.title)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    username = db.Column(db.String(64), db.ForeignKey('user.username'))
    question = db.Column(db.String(100))
    answer = db.Column(db.String(300))
    def __repr__(self):
        return '<Quiz {}>'.format(self.title)

class Current(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(150))
    details = db.Column(db.String(500))
    date = db.Column(db.String(64))

    def repr(self):
        return '<Current {}>'.format(self.title)

class Random(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    username = db.Column(db.String(64), db.ForeignKey('user.username'))
    title = db.Column(db.String(150))
    details = db.Column(db.String(5000))

    def repr(self):
        return '<Random {}>'.format(self.title)

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(150))
    details = db.Column(db.String(5000))
    date = db.Column(db.String(64))

    def repr(self):
        return '<About {}>'.format(self.title)
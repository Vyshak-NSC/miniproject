from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from time import strftime

class User(db.Model, UserMixin):
    """User model for storing user related information"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    categories = db.relationship("Category", backref="user", lazy=True)
    articles = db.relationship("Article", backref="user", lazy=True)
    notification = db.relationship("Notification", backref="user", lazy=True)
    target = db.relationship("Target", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Category(db.Model):
    """ Category model for storing  category of expenses """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    value = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = strftime("%A %d-%m-%Y")
    exp_type = db.Column(db.String(64),nullable=False)

    def __repr__(self):
        return '<Category {}, {}>'.format(self.name,self.user)


class Article(db.Model):
    """Article model for saving articles about money """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.String(5000))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # user = db.relationship("User", backref=db.backref("articles", lazy="dynamic"))


class Target(db.Model):
    """Target represents the expense targets set by users"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.today)  # Auto fill start date
    end_date = db.Column(db.Date, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Notification(db.Model):
    """Notification represents email notification to the User"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    date_generated = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    def __repr__(self):
        return '<Notification {}>'.format(self.title)

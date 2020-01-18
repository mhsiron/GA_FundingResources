from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    group = db.Column(db.String(20))

    funding_resources_authored = db.relationship('FundingResources',
                                    foreign_keys='FundingResources.user_id',
                                    backref='user', lazy='dynamic')

    comments_posted = db.relationship('FundingResourceComments',
                                      foreign_keys='FundingResourceComments.user_id',
                                      backref='user',
                                      lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def make_admin(self):
        self.group = "admin"

    def is_admin(self):
        return self.group == "admin"

    def make_editor(self):
        self.group = "editor"

import enum
class Main_Categories(enum.Enum):
    research = "research"
    organization =  "organization"
    personal = "personal"

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        item = cls(item) \
            if not isinstance(item, cls) \
            else item  # a ValueError thrown if item is not defined in cls.
        return item.value

class Alert_Type(enum.Enum):
    primary = "primary"
    secondary =  "secondary"
    success = "success"
    danger = "danger"
    warning = "warning"
    info = "info"
    dark = "dark"

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        item = cls(item) \
            if not isinstance(item, cls) \
            else item  # a ValueError thrown if item is not defined in cls.
        return item.value

class FundingResources(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name  = db.Column(db.String(120), index=True, unique=True)
    source = db.Column(db.String(120))
    URL = db.Column(db.String(300))
    deadline = db.Column(db.Date())
    description = db.Column(db.String())
    criteria = db.Column(db.String())
    amount = db.Column(db.Float(precision=2))
    restrictions = db.Column(db.String())
    timeline = db.Column(db.String())
    point_of_contact = db.Column(db.String())
    ga_contact = db.Column(db.String())
    keywords = db.Column(db.String())
    main_cat = db.Column(db.Enum(Main_Categories))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_enabled = db.Column(db.Boolean())

    comments_posted = db.relationship('FundingResourceComments',
                                      foreign_keys='FundingResourceComments.funding_id',
                                      backref='resource',
                                      lazy='dynamic')

    def disable(self):
        self.is_enabled = False

    def enable(self):
        self.is_enabled = True

class FundingResourceComments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posted_date = db.Column(db.Date())
    comment = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    funding_id = db.Column(db.Integer, db.ForeignKey('funding_resources.id'))
    comment_type = db.Column(db.Enum(Alert_Type))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


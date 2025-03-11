from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean)

    def __repr__(self):
        return f'User({self.username})'


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idblock = db.Column(db.String(100), unique=True, nullable=True)
    short_title = db.Column(db.String(50), unique=True, nullable=True)
    img = db.Column(db.String(150), unique=True, nullable=True)
    altimg = db.Column(db.String(50), unique=True, nullable=True)
    title = db.Column(db.String(100), unique=True, nullable=True)
    contenttext = db.Column(db.String(1000), unique=True, nullable=True)
    author = db.Column(db.String(100), unique=True, nullable=True)
    timestampdata = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean)

    def __repr__(self):
        return f'Block({self.idblock}, {self.title})'

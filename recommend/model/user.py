from flask_login import UserMixin
from recommend import db, user_role

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    roles = db.relationship('Role', secondary=user_role, backref='us')




    def __init__(self, id, username, password, roles):
        self.id = id
        self.username = username
        self.password = password
        self.roles = roles

    def __repr__(self):
        return '<User %r>' % self.username

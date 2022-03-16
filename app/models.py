from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


# create script for changes:  flask db migrate -m "changes message"
# apply changes to db:  flask db upgrade

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_login = db.Column(db.Boolean, default=True)
    first_edit = db.Column(db.Boolean, default=True)
    profile_icon = db.Column(db.String(255))
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(255), index=True, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    status = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    icon = db.Column(db.String(255))
    marked_for_complete = db.Column(db.Boolean)

    def __repr__(self):
        return '<Task {}>'.format(self.title)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

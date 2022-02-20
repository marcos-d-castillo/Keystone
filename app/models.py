import enum

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


# create script for changes:  flask db migrate -m "changes message"
# applies changes to db:  flask db upgrade
class StatusEnum(enum.Enum):
    backlog = 1
    todo = 2
    complete = 3
    daily = 4


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_login = db.Column(db.Boolean, default=True)
    first_edit = db.Column(db.Boolean, default=True)
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
    status = db.Column(db.Enum(StatusEnum))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Task {}>'.format(self.title)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# # Daily tasks
# t = Task(title='Stretch', description='Take at least 15 minutes to stretch\n\n*Don\'t forget to set your activity tracker', status='daily', user_id=3)
# t1 = Task(title='Read', description='30 minutes before bed', status='daily', user_id=3)
# t2 = Task(title='Meditate', description='Focus on breathing for 5 minutes', status='daily', user_id=3)
#
# # Todos with set date
# td = datetime.datetime.now()
# t3 = Task(title='Dinner with Aki', description='Figure out what to bring!', status='todo', date=td, user_id=3)

# u = User.query.get(3)
# u.first_login = True
# u.first_edit = True
# db.session.commit()

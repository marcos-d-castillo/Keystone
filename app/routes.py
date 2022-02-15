from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, AddTaskForm
from app.models import User, Task, StatusEnum
from app import app, db
import datetime

# TODO:
#         - Add warning before task delete
#         - Merge Add / Edit Task?
#         - Hover tool tips
#         - User Profile Page
#         - Dates and Times (for microservice)
#         - API (for microservice)
#         - Add theme to user table to be able to set theme colors
#         - Email for notification alerts
#         - Tour of Keystone
#         - Email password reset
#         - Error Handling
#
#         Optional:
#                       - User Notifications


@app.route('/')
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    today = datetime.datetime.today()
    if current_user.first_login:
        flash('A demonstration of the Keystone workflow is available in the dropdown menu in the upper right corner. '
              'It can be viewed anytime.')
        user = User.query.get(current_user.id)
        user.first_login = False
        db.session.commit()

    tasks = current_user.tasks

    return render_template('dashboard.html', title='Dashboard', tasks=tasks, time=today, status=StatusEnum)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')

            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        view_to_be_accessed = request.args.get('next')
        if not view_to_be_accessed or url_parse(view_to_be_accessed).netloc != '':
            view_to_be_accessed = url_for('dashboard')

        return redirect(view_to_be_accessed)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to Keystone!')

        return redirect(url_for('login'))

    return render_template('registration.html', title='Register', form=form)


@app.route('/backlog', methods=['GET', 'POST'])
@login_required
def backlog():
    tasks = current_user.tasks

    return render_template('backlog.html', title='Backlog', tasks=tasks, status=StatusEnum)


@app.route('/addTask', methods=['GET', 'POST'])
@login_required
def addTask():
    form = AddTaskForm()

    if form.validate_on_submit():
        status = StatusEnum.todo if request.args.get('moveToTodo') else StatusEnum.backlog
        task = Task(title=form.title.data, description=form.description.data, date=form.date.data,
                    status=status, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash(f'Task created: {task.title}')

        print(request.args.keys())
        return redirect(url_for('dashboard'))

    return render_template('addTask.html', title='Add Task', form=form)


@app.route('/editTask', methods=['GET', 'POST'])
@login_required
def editTask():
    task = Task.query.get(request.args.get('taskId'))
    isReady = (task.status == StatusEnum.todo)
    form = AddTaskForm(title=task.title, description=task.description, date=task.date, moveToTodo=isReady)

    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(task)
            db.session.commit()
            flash(f'Task deleted')

            return redirect(url_for('dashboard'))

        status = StatusEnum.todo if request.args.get('moveToTodo') else StatusEnum.backlog

        task.title = form.title.data
        task.description = form.description.data
        task.date = form.date.data
        task.status = status

        db.session.commit()
        flash(f'Task edited: {task.title}')

        return redirect(url_for('dashboard'))

    return render_template('editTask.html', title='Edit Task', form=form)

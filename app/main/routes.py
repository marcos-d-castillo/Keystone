import datetime

from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import AddTaskForm
from app.models import User, Task, StatusEnum


# TODO:
#         - Dates and Times (for microservice)
#         - API (for microservice)
#         - Add theme to user table to be able to set theme colors
#         - Add warning before task delete
#         - Tour of Keystone
#         - Hover tool tips
#         - User Profile Page
#         - Email for notification alerts <--- Need to view both original tutorial and app restructure tutorial
#         - Email password reset
#         - Merge Add / Edit Task?
#
#         Optional:
#                       - User Notifications


@bp.route('/')
@bp.route('/dashboard', methods=['GET', 'POST'])
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


@bp.route('/backlog', methods=['GET', 'POST'])
@login_required
def backlog():
    tasks = current_user.tasks

    return render_template('backlog.html', title='Backlog', tasks=tasks, status=StatusEnum)


@bp.route('/progressBoard', methods=['GET', 'POST'])
@login_required
def progressBoard():
    tasks = current_user.tasks

    return render_template('progressBoard.html', title='Progress Board', tasks=tasks, status=StatusEnum)


@bp.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    tasks = current_user.tasks

    return  render_template('calendar.html', title='Calendar', tasks=tasks, status=StatusEnum)


@bp.route('/daily', methods=['GET', 'POST'])
@login_required
def daily():
    tasks = current_user.tasks

    return render_template('daily.html', title='Daily', tasks=tasks, status=StatusEnum)


@bp.route('/addTask', methods=['GET', 'POST'])
@login_required
def addTask():
    form = AddTaskForm()

    if form.validate_on_submit():
        status = StatusEnum.todo if form.moveToTodo.data else StatusEnum.backlog
        print('DATE: ', form.date.data)
        task = Task(title=form.title.data, description=form.description.data, date=form.date.data,
                    status=status, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash(f'Task created: {task.title}')

        print(request.args.keys())
        return redirect(url_for('main.dashboard'))

    return render_template('addTask.html', title='Add Task', form=form)


@bp.route('/editTask', methods=['GET', 'POST'])
@login_required
def editTask():
    if current_user.first_edit:
        flash('Here is where you can edit and delete tasks. Remember: Editing a task is reversible, '
              'deleting is permanent!')
        user = User.query.get(current_user.id)
        user.first_edit = False
        db.session.commit()

    task = Task.query.get(request.args.get('taskId'))
    isReady = (task.status == StatusEnum.todo)
    form = AddTaskForm(title=task.title, description=task.description, date=task.date, moveToTodo=isReady)

    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(task)
            db.session.commit()
            flash(f'Task deleted')

            return redirect(url_for('main.dashboard'))

        status = StatusEnum.todo if form.moveToTodo.data else StatusEnum.backlog

        task.title = form.title.data
        task.description = form.description.data
        task.date = form.date.data
        task.status = status

        db.session.commit()
        if request.args.get('moveToTodo'):
            flash("Remember not to overload yourself with too many tasks!")

        flash(f'Task edited: {task.title}')

        return redirect(url_for('main.dashboard'))

    return render_template('editTask.html', title='Edit Task', form=form)

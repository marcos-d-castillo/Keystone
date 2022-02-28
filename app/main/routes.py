import datetime

import requests
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import AddTaskForm
from app.models import User, Task, StatusEnum

# TODO:
#         - Add warning before task delete
#         - Tour of Keystone
#         - Hover tool tips
#         - User Profile Page
#         - Email for notification alerts <--- Need to view both original tutorial and app restructure tutorial
#         - Email password reset
#         - Merge Add / Edit Task?



getIconsUrl = 'https://icon-depot.herokuapp.com/icons'


def getIcons():
    iconNames = ["face", "favorite", "shopping_cart", "star_rate", "flight_takeoff", "emoji_emotions", "sentiment_neutral",
             "emoji_people", "emoji_nature", "self_improvement", "hiking", "catching_pokemon", "sports_martial_arts"]

    data = {"icon_list": ["face", "favorite", "shopping_cart", "star_rate", "flight_takeoff", "emoji_emotions", "sentiment_neutral",
             "emoji_people", "emoji_nature", "self_improvement", "hiking", "catching_pokemon", "sports_martial_arts"]}

    headers = {"Content-Type": "application/json"}

    r = requests.post(getIconsUrl, json=data, headers=headers).json()
    icons = [(None, " -")]

    counter = 0
    for icon in r['html']:
        icons.append((icon, iconNames[counter]))
        counter += 1

    return icons


icons = getIcons()


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
    form.icon.choices = [(icon[1], icon[1].replace("_", " ")) for icon in icons]
    iconsToDisplay = [icon[0] for icon in icons if icon[0] is not None]

    if form.validate_on_submit():
        status = None
        if form.status.data:
            status = getTaskStatus(form.status.data)
        task = Task(title=form.title.data, description=form.description.data, date=form.date.data,
                    status=status, icon=form.icon.data, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash(f'Task created: {task.title}')

        return redirect(url_for('main.dashboard'))

    return render_template('addTask.html', title='Add Task', form=form, icons=iconsToDisplay)


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
    # print(task.icon.data)
    # if not task.icon or '<' not in task.icon:
    #     icon = getIconHtml(task.icon)
    # else:
    #     icon = task.icon
    form = AddTaskForm(title=task.title, description=task.description, date=task.date, status=task.status, icon=task.icon)
    form.icon.choices = icons
    # form.icon = task.icon

    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(task)
            db.session.commit()
            flash(f'Task deleted')

            return redirect(url_for('main.dashboard'))

        if type(task.status) is StatusEnum:
            status = task.status
        else:
            status = getTaskStatus(task.status)

        task.title = form.title.data
        task.description = form.description.data
        task.date = form.date.data
        task.status = status
        task.icon = form.icon.data

        db.session.commit()

        flash(f'Task edited: {task.title}')

        return redirect(url_for('main.dashboard'))

    return render_template('editTask.html', title='Edit Task', form=form)


def getTaskStatus(status):
    if status == 'backlog':
        return StatusEnum.backlog
    elif status == 'todo':
        return StatusEnum.todo
    elif status == 'complete':
        return StatusEnum.complete
    elif status == 'daily':
        return StatusEnum.daily


def getIconHtml(iconName):
    for iconTuple in icons:
        if iconTuple[1] == iconName:
            return iconTuple[0]

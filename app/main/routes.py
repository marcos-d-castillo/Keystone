import datetime

import requests
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import TaskForm, DailyTaskForm
from app.models import User, Task

getIconsUrl = 'https://icon-depot.herokuapp.com/icons'


# On start up, gets icon HTML from Icon Depot, a microservice provided by my teammate
def getIcons():
    tagNames = ["face", "favorite", "shopping_cart", "star_rate", "flight_takeoff", "sentiment_very_satisfied",
                "sentiment_satisfied", "sentiment_neutral", "sentiment_dissatisfied", "sentiment_very_dissatisfied",
                "emoji_people", "emoji_nature", "self_improvement", "hiking", "catching_pokemon",
                "sports_martial_arts"]

    choiceNames = ['Face', 'Heart', 'Shopping Cart', 'Star', 'Flight', 'Very Happy', 'Happy', 'Neutral', 'Sad',
                   'Very Sad', 'Person', 'Nature', 'Meditation', 'Hiking', 'Pokemon', 'Martial Arts']

    data = {"icon_list": tagNames}

    headers = {"Content-Type": "application/json"}

    response = requests.post(getIconsUrl, json=data, headers=headers).json()
    newIconDict = {}

    for i in range(len(response['html'])):
        newIconDict[choiceNames[i]] = response['html'][i]

    return newIconDict


iconDict = getIcons()

# Create list of tuples for icon select field choices in the task forms
selectFieldChoices = [(None, " -")]
for iconName in iconDict.keys():
    selectFieldChoices.append((iconName, iconName))


@bp.route('/')
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    today = datetime.datetime.today()
    info = 'This is the landing page of the application every time you log in and the list of things to accomplish ' \
           'for the day.\n\nHere you can add a new task by clicking the Add Task button on the lower left. You can also ' \
           'edit a To-do task by clicking on the task title. Daily tasks can be edited from the Daily page. '
    if current_user.first_login:
        flash('Welcome to Keystone!\n\nYou will find a question mark icon (?) at the lower right of each page. Here you '
              'will find a description of what you can do on the page and useful tips. Check them out as you explore '
              '(or not :-)), they can be viewed at any time, as many times as you need!')
        user = User.query.get(current_user.id)
        user.first_login = False
        db.session.commit()

    tasks = current_user.tasks

    return render_template('dashboard.html', title='Dashboard', tasks=tasks, time=today, iconDict=iconDict, info=info)


@bp.route('/progressBoard', methods=['GET', 'POST'])
@login_required
def progressBoard():
    tasks = current_user.tasks
    info = 'This gives you a high-level view on what you would like to do, what you\'ve committed to and what you ' \
           'have accomplished.\n\nYou can add a new task by clicking the Add Task button on the lower left. You can ' \
           'also edit a task by clicking on the task title. To move a task to another column, click the task title to ' \
           'edit and select a new status for the task. '

    return render_template('progressBoard.html', title='Progress Board', tasks=tasks, iconDict=iconDict, info=info)


@bp.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    tasks = current_user.tasks
    info = 'This view allows you to see tasks that you\'ve set as To-do and provided a date for on a calendar.\n\nYou ' \
           'can add a new task by clicking the Add Task button on the lower left. You can also edit a task by ' \
           'clicking on it in the calendar. '

    return render_template('calendar.html', title='Calendar', tasks=tasks, info=info)


@bp.route('/daily', methods=['GET', 'POST'])
@login_required
def daily():
    tasks = current_user.tasks
    info = 'Here you can manage tasks that repeat every day. A tip we like to give new users is to think about what ' \
           'you would need to do to consider tomorrow a good day? We also like to remind users that sometimes less is ' \
           'more. Don\'t overwhelm yourself with too many things to do.\n\n You can add a new daily task by clicking ' \
           'the Add New Task button. You can edit a daily task by clicking on the task title. '

    return render_template('daily.html', title='Daily', tasks=tasks, iconDict=iconDict, info=info)


@bp.route('/addTask', methods=['GET', 'POST'])
@login_required
def addTask():
    form = TaskForm()
    form.icon.choices = selectFieldChoices
    info = 'This form will create a new task. If you have an idea of something that you would like to do but don\'t ' \
           'have all of the details worked out, that\'s fine! You can just give it a name and leave it in the backlog ' \
           'for now.\n\nDescriptions aren\'t necessary but helpful for providing more information to complete the task. ' \
           'Providing a date will allow the application to show the task on the dashboard on that date and make the ' \
           'task viewable on the calendar (once it\'s set as To-Do). The task status helps you keep track of your ' \
           'progress. Also, setting a task as To-Do with a specified date allows it to appear in the dashboard and ' \
           'calendar.\n\nFinally, an icon can be set for a task if you would like to add some flair to your lists. ' \
           'These don\'t affect how the task is tracked. '

    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, date=form.date.data,
                    status=form.status.data, icon=form.icon.data, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash(f'Task created: {task.title}')

        return redirect(request.referrer)

    return render_template('task.html', title='Add Task', form=form, formType='Add Task', iconDict=iconDict, info=info)


@bp.route('/editTask', methods=['GET', 'POST'])
@login_required
def editTask():
    info = 'Here is where you can edit and delete your task. Remember: Editing a task is reversible, deleting is ' \
           'permanent! '

    if current_user.first_edit:
        flash(info)
        user = User.query.get(current_user.id)
        user.first_edit = False
        db.session.commit()

    task = Task.query.get(request.args.get('taskId'))
    form = TaskForm(title=task.title, description=task.description, date=task.date, status=task.status,
                    icon=task.icon)
    form.icon.choices = selectFieldChoices

    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(task)
            db.session.commit()
            flash(f'Task deleted')

            return redirect(url_for('main.progressBoard'))

        task.title = form.title.data
        task.description = form.description.data
        task.date = form.date.data
        task.status = form.status.data
        task.icon = form.icon.data

        db.session.commit()

        flash(f'Task edited: {task.title}')

        return redirect(url_for('main.progressBoard'))

    return render_template('task.html', title='Edit Task', form=form, formType='Edit Task', iconDict=iconDict,
                           info=info)


@bp.route('/addDailyTask', methods=['GET', 'POST'])
@login_required
def addDailyTask():
    form = DailyTaskForm()
    form.icon.choices = selectFieldChoices
    info = 'You can use this form to create a new daily task. Daily tasks are tasks that are part of your daily ' \
           'routine and repeat every day.\n\nThe only thing necessary to create a new task is a title but adding a ' \
           'description can be helpful. If you can\'t think of a description now, no worries, you can always edit the ' \
           'task and add one later. Adding an icon is totally optional and doesn\'t affect the task in any way, ' \
           'so have fun with it (or not :-)).\n\nAgain, be mindful of how many tasks you add to your daily routine. ' \
           'Overwhelming yourself is going to help create and maintain habits! '

    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data,
                    status='daily', icon=form.icon.data, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash(f'Task created: {task.title}')

        return redirect(url_for('main.daily'))

    return render_template('dailyTask.html', title='Add Daily Task', form=form, formType='Add Daily Task',
                           iconDict=iconDict, info=info)


@bp.route('/editDailyTask', methods=['GET', 'POST'])
@login_required
def editDailyTask():
    task = Task.query.get(request.args.get('taskId'))
    form = DailyTaskForm(title=task.title, description=task.description, icon=task.icon)
    form.icon.choices = selectFieldChoices
    info = 'This is where you edit or delete your daily task. If you would like to rename a task or add or update a ' \
           'description this is where you do it!\n\nRemember: Editing a task is reversible, deleting is permanent! '

    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(task)
            db.session.commit()
            flash(f'Daily Task deleted')

            return redirect(url_for('main.daily'))

        task.title = form.title.data
        task.description = form.description.data
        task.icon = form.icon.data

        db.session.commit()

        flash(f'Task edited: {task.title}')

        return redirect(url_for('main.daily'))

    return render_template('dailyTask.html', title='Edit Daily Task', form=form, formType='Edit Daily Task',
                           iconDict=iconDict, info=info)

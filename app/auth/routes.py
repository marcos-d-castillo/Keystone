from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')

            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        view_to_be_accessed = request.args.get('next')
        if not view_to_be_accessed or url_parse(view_to_be_accessed).netloc != '':
            view_to_be_accessed = url_for('main.dashboard')

        return redirect(view_to_be_accessed)

    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to Keystone!')

        return redirect(url_for('auth.login'))

    return render_template('auth/registration.html', title='Register', form=form)

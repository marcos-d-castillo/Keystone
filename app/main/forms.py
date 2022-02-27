from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Optional
from app.models import StatusEnum


class AddTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', validators=[Optional()])
    status = SelectField(u'Task Status', choices=[('backlog', 'Backlog'), ('todo', 'To-Do'), ('complete', 'Complete'), ('daily', 'Daily')], default='backlog')
    icon = SelectField(u'(Optional) Add Icon')
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')

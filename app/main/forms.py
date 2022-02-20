from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Optional


class AddTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', validators=[Optional()])
    moveToTodo = BooleanField('Ready for To-do?')
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class BookForm(FlaskForm):
    book = StringField('Title of activity', validators=[DataRequired()])
    author = StringField('Title of activity', validators=[DataRequired()])
    book_size = IntegerField('Duration', validators=[DataRequired()])
    name_book = StringField('List of collaborators')
    genre = StringField('List of collaborators')
    start_date = DateField('Start date')
    end_date = DateField('End date')
    is_finished = BooleanField('Is finished')
    submit = SubmitField('Save')
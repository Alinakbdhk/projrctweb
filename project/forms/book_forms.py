from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class BookForm(FlaskForm):
    book = StringField('Название книги', validators=[DataRequired()])
    work_size = IntegerField('Время прочтения', validators=[DataRequired()])
    collaborators = StringField('Автор, жанр')
    start_date = DateField('Start date')
    end_date = DateField('End date')
    is_finished = BooleanField('Прочитано?')
    submit = SubmitField('Сохранить')
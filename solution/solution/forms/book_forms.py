from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class BookForm(FlaskForm):
    book = StringField('Название книги', validators=[DataRequired()])
    book_size = IntegerField('Кол-во страниц', validators=[DataRequired()])
    author = StringField('Автор')
    genre = StringField('Жанр')
    start_date = DateField('Начало чтения')
    end_date = DateField('Конец прочтения')
    is_finished = BooleanField('Состояние(окончена или нет)')
    submit = SubmitField('Save')
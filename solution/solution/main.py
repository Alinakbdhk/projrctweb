from flask import Flask, render_template, redirect, abort, request
import datetime

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.users import User
from data.books import Books
from forms.user_forms import RegisterForm, LoginForm
from forms.book_forms import BookForm
import sys
import requests
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    books = db_sess.query(Books).all()
    return render_template('index.html', books=books)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        for key, value in form.data.items():
            if key not in ('submit', 'password', 'password_again'):
                setattr(user, key, value)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/books',  methods=['GET', 'POST'])
@login_required
def add_books():
    form = BookForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = Books()
        for field in form:
            if hasattr(book, field.name):
                setattr(book, field.name, field.data)
        book.team_leader = current_user.id
        db_sess.add(book)
        db_sess.commit()
        return redirect('/')
    if not form.start_date.data:
        form.start_date.data = datetime.datetime.now()
    if not form.end_date.data:
        form.end_date.data = datetime.datetime.now()
    return render_template('work.html', title='Добавление работ',
                           form=form)

@app.route('/books/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_books(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Books).filter(Books.id == id)
    if current_user.id == 1:
        book = book.first()
    else:
        book = book.filter(Books.team_leader_user == current_user).first()
    if not book:
        abort(404)
    form = BookForm()
    if request.method == "GET":
        for field in form:
            if hasattr(book, field.name):
                field.data = getattr(book, field.name)
    if form.validate_on_submit():
        for field in form:
            if hasattr(book, field.name):
                setattr(book, field.name, field.data)
        db_sess.commit()
        return redirect('/')
    return render_template('work.html',
                            title='Edit book',
                            form=form
                            )


@app.route('/books_delete/<int:id>',  methods=['GET', 'POST'])
@login_required
def books_delete(id):
        db_sess = db_session.create_session()
        book = db_sess.query(Books).filter(Books.id == id)
        if current_user.id == 1:
            book = book.first()
        else:
            book = book.filter(Books.team_leader_user == current_user).first()
        if book:
            db_sess.delete(book)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')

@app.route('/map')
def map():
    SCREEN_SIZE = [600, 450]

    class Example(QWidget):
        SCALE_INITIAL = 0.002
        SCALE_FACTOR = 2
        SCALE_MIN = 0.000125
        SCALE_MAX = 65
        LONG = 37.608902
        LAT = 55.751638

        def __init__(self):
            super().__init__()
            self.long = self.LONG
            self.lat = self.LAT
            self.scale = self.SCALE_INITIAL
            self.initUI()
            self.getImage()

        def getImage(self):
            map_request = "http://static-maps.yandex.ru/1.x/"
            params = {
                'll': f'{self.long},{self.lat}',
                'spn': f'{self.scale},{self.scale}',
                'l': 'map'
            }
            response = requests.get(map_request, params=params)

            if not response:
                print("Ошибка выполнения запроса:")
                print(map_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)

            self.pixmap = QPixmap()
            self.pixmap.loadFromData(response.content)
            self.image.setPixmap(self.pixmap)

        def initUI(self):
            self.setGeometry(100, 100, *SCREEN_SIZE)
            self.setWindowTitle('Отображение карты')
            self.image = QLabel(self)
            self.image.move(0, 0)
            self.image.resize(600, 450)

        def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
            keys = {
                Qt.Key_PageUp, Qt.Key_PageDown,
                Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right
            }
            if event.key() == Qt.Key_PageUp:
                self.scale /= self.SCALE_FACTOR
            elif event.key() == Qt.Key_PageDown:
                self.scale *= self.SCALE_FACTOR
            if self.scale > self.SCALE_MAX:
                self.scale = self.SCALE_MAX
            elif self.scale < self.SCALE_MIN:
                self.scale = self.SCALE_MIN
            elif event.key() == Qt.Key_Up:
                self.lat += self.scale
            elif event.key() == Qt.Key_Down:
                self.lat -= self.scale
            elif event.key() == Qt.Key_Left:
                self.long -= self.scale
            elif event.key() == Qt.Key_Right:
                self.long += self.scale
            if self.long > 180:
                self.long -= 360
            elif self.long < -180:
                self.long += 360
            if self.lat > 85:
                self.lat = 85
            elif self.lat < -85:
                self.lat = -85
            if event.key() in keys:
                return(getImage())


def main():
    db_session.global_init("db/db.db")
    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    main()

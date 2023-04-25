from flask import Flask, render_template, redirect, abort, request
import datetime

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from solution.data import db_session
from solution.data.users import User
from solution.data.book import Book
from solution.forms.user_forms import RegisterForm, LoginForm
from solution.forms.book_forms import BookForm

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
def index(books=None):
    db_sess = db_session.create_session()
    books = db_sess.query(Book).all()
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
        book = Book()
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
    return render_template('work.html', title='Добавление книг',
                           form=form)

@app.route('/books/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_books(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)
    if current_user.id == 1:
        book = book.first()
    else:
        book = book.filter(Book.team_leader_user == current_user).first()
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
        book = db_sess.query(Book).filter(Book.id == id)
        if current_user.id == 1:
            book = book.first()
        else:
            book = book.filter(Book.team_leader_user == current_user).first()
        if book:
            db_sess.delete(book)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')


def main():
    db_session.global_init("db/db.db")
    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    main()

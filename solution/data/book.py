import sqlalchemy as sa
from sqlalchemy import orm
import datetime

from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase):
    __tablename__ = 'books'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    team_leader = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=True)
    author = sa.Column(sa.String, nullable=True)
    book = sa.Column(sa.String, nullable=True)
    book_size = sa.Column(sa.Integer, nullable=True)
    genre = sa.Column(sa.String, nullable=True)
    start_date = sa.Column(sa.DateTime, nullable=True)
    end_date = sa.Column(sa.DateTime, nullable=True)
    is_finished = sa.Column(sa.Boolean, nullable=True)

    team_leader_user = orm.relationship('User')

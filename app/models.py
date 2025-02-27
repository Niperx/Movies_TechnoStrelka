from datetime import datetime, timezone
from hashlib import md5
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
  return db.session.get(User, int(id))

film_tag = sa.Table(
    "film_tag",
    db.metadata,
    sa.Column("film_id", sa.Integer, sa.ForeignKey("film.id"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tag.id"), primary_key=True)
)

film_review = sa.Table(
    "film_review",
    db.metadata,
    sa.Column("film_id", sa.Integer, sa.ForeignKey("film.id"), primary_key=True),
    sa.Column("review_id", sa.Integer, sa.ForeignKey("review.id"), primary_key=True)
)


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    ratings: so.Mapped[List["Rating"]] = so.relationship(back_populates="user", lazy="dynamic")
    comments: so.Mapped[List["Comment"]] = so.relationship(back_populates="user", lazy="dynamic")

    search_history: so.Mapped[List["SearchHistory"]] = so.relationship(
        back_populates="user",
        lazy="dynamic"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Film(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    film_id: so.Mapped[int] = so.mapped_column(unique=True, nullable=False)
    title: so.Mapped[str] = so.mapped_column(sa.String(200), index=True, nullable=False)
    year: so.Mapped[Optional[int]] = so.mapped_column()
    rating: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(500))
    shortDescription: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300))
    poster_Url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300))
    poster_Url_preview: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300))
    cover_Url:  so.Mapped[Optional[str]] = so.mapped_column(sa.String(300))
    wed_Url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300))
    genres: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300))
    countries: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300))
    ai_plot: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    ai_characters: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    ai_moment: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    ai_idea: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    ai_impress: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    review: so.Mapped[List["Review"]] = so.relationship(
        "Review",
        secondary=film_review,
        back_populates="films"
    )

    tags: so.Mapped[List["Tag"]] = so.relationship(
        "Tag",
        secondary=film_tag,
        back_populates="films"
    )

    ratings: so.Mapped[List["Rating"]] = so.relationship(back_populates="film", lazy="dynamic")
    comments: so.Mapped[List["Comment"]] = so.relationship(back_populates="film", lazy="dynamic")
    search_history: so.Mapped[List["SearchHistory"]] = so.relationship(back_populates="film", lazy="dynamic")

    def __repr__(self):
        return f"<Film(film_id={self.film_id}, name_ru={self.title}, year={self.year}, rating={self.rating})>"


class Tag(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True, nullable=False, index=True)

    # Связь с фильмами через промежуточную таблицу
    films: so.Mapped[List["Film"]] = so.relationship(
        "Film",
        secondary=film_tag,
        back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class Review(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    text: so.Mapped[str] = so.mapped_column(sa.Text, unique=True, nullable=False, index=True)

    # Связь с фильмами через промежуточную таблицу
    films: so.Mapped[List["Film"]] = so.relationship(
        "Film",
        secondary=film_review,
        back_populates="review"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


# Модель оценки
class Rating(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    film_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("film.id"), nullable=False)
    score: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)  # Оценка (например, от 1 до 5)

    # Связи
    user: so.Mapped["User"] = so.relationship(back_populates="ratings")
    film: so.Mapped["Film"] = so.relationship(back_populates="ratings")

    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, film_id={self.film_id}, score={self.score})>"

# Модель комментария
class Comment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    film_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("film.id"), nullable=False)
    text: so.Mapped[str] = so.mapped_column(sa.String(1000), nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, index=True, default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    user: so.Mapped["User"] = so.relationship(back_populates="comments")
    film: so.Mapped["Film"] = so.relationship(back_populates="comments")

    def __repr__(self):
        return f"<Comment(user_id={self.user_id}, film_id={self.film_id}, text={self.text[:20]})>"


class SearchHistory(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    query: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)  # Запрос пользователя
    timestamp: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=lambda: datetime.now(timezone.utc)
    )  # Время поиска

    film_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey("film.id"), nullable=True, default=None
    )  # ID найденного фильма (опционально)

    # Связи
    user: so.Mapped["User"] = so.relationship(back_populates="search_history")
    film: so.Mapped["Film"] = so.relationship(back_populates="search_history")

    def __repr__(self):
        return f"<SearchHistory {self.query} by User {self.user_id}>"

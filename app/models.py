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


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

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
    ai_plot: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000))
    ai_characters: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000))
    ai_moment: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000))
    ai_idea: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000))
    ai_impress: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000))

    tags: so.Mapped[List["Tag"]] = so.relationship(
        "Tag",
        secondary=film_tag,
        back_populates="films"
    )


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
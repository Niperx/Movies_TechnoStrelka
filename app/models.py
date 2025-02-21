from datetime import datetime, timezone
from hashlib import md5
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
  return db.session.get(User, int(id))


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
    year: so.Mapped[Optional[int]] = so.mapped_column(comment='opt')
    rating: so.Mapped[Optional[float]] = so.mapped_column(sa.Float, comment='opt')
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(500), comment='opt')
    shortDescription: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), comment='opt')
    poster_Url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), comment='opt')
    poster_Url_preview: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), comment='opt')
    cover_Url:  so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), comment='opt')
    wed_Url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), comment='opt')
    genres: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), comment='opt')
    countries: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), comment='opt'),
    tags: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), comment='opt'),
    ai_plot: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000), comment='opt1'),
    ai_characters: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000), comment='opt2'),
    ai_moment: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000), comment='opt3'),
    ai_idea: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000), comment='opt4'),
    ai_impress: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000), comment='opt5')

    def __repr__(self):
        return f"<Film(film_id={self.film_id}, name_ru={self.title}, year={self.year}, rating={self.rating})>"
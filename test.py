import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import Film
from app import db, app

app.app_context().push()
films = db.session.scalars(
        sa.select(Film).options(so.subqueryload(Film.review))
    ).all()

genres = []
for film in films:
    genres_list = film.genres.split(", ")
    for tag in genres_list:
        if not tag in genres:
            genres.append(tag)
print(genres)

# t = 'Шышки, Красиво, Белый'
#
# print(t.lower())
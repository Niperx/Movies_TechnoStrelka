from app.models import Film, Review
from app import app, db, model
import sqlalchemy as sa
import sqlalchemy.orm as so

from search import es

def get_films():
    films = db.session.scalars(
        sa.select(Film).options(so.subqueryload(Film.review))
    ).all()

    films_data = []
    for film in films:
        reviews = [review.text for review in film.review]
        reviews_text = " ".join(reviews)

        film_data = {
            "id": film.id,
            "title": film.title,
            "genres": film.genres,
            "description": film.description,
            "ai_moment": film.ai_moment,
            "poster_Url": film.poster_Url,
            "shortDescription": film.shortDescription,
            "reviews": reviews_text,
        }
        films_data.append(film_data)

    return films_data


def index_films(films):
    for film in films:
        description_vector = model.encode(film["description"] or "").tolist()
        ai_moment_vector = model.encode(film["ai_moment"] or "").tolist()
        review_vector = model.encode(film["reviews"]).tolist()

        es.index(
            index="films",
            id=film["id"],
            document={
                "title": film["title"],
                "description": film["description"] or "",
                "description_vector": description_vector,
                "genres": film["genres"].split(", "),
                "ai_moment": film["ai_moment"] or "",
                "ai_moment_vector": ai_moment_vector,
                "poster_Url": film["poster_Url"] or "",
                "shortDescription": film["shortDescription"] or "",
                "reviews": film["reviews"],
                "review_vector": review_vector
            }
        )
    print('Индексация прошла успешно!')


if __name__ == "__main__":
    app.app_context().push()
    films_data = get_films()

    index_films(films_data)

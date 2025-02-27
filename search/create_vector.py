from app.models import Film, Review
from app import app, db, model
import sqlalchemy as sa
import sqlalchemy.orm as so

from search import es

def get_films():
    # Получаем все фильмы
    films = db.session.scalars(
        sa.select(Film).options(so.subqueryload(Film.review))
    ).all()

    # Формируем данные для индексации
    films_data = []
    for film in films:
        reviews = [review.text for review in film.review]
        reviews_text = " ".join(reviews)

        # Формируем словарь с данными фильма
        film_data = {
            "id": film.id,
            "title": film.title,
            "genres": film.genres,
            "description": film.description,
            "ai_moment": film.ai_moment,
            "poster_Url": film.poster_Url,
            "shortDescription": film.shortDescription,
            "reviews": reviews_text,  # Объединённые обзоры
        }
        films_data.append(film_data)

    return films_data


# Функция для индексации фильмов
def index_films(films):
    for film in films:
        # Генерация векторов для текстовых полей
        description_vector = model.encode(film["description"] or "").tolist()
        ai_moment_vector = model.encode(film["ai_moment"] or "").tolist()
        review_vector = model.encode(film["reviews"]).tolist()

        # Индексация фильма в Elasticsearch
        es.index(
            index="films",
            id=film["id"],
            document={
                "title": film["title"],
                "description": film["description"] or "",
                "description_vector": description_vector,
                "genres": film["genres"].split(", "),  # Разделяем жанры по запятой
                "ai_moment": film["ai_moment"] or "",
                "ai_moment_vector": ai_moment_vector,
                "poster_Url": film["poster_Url"] or "",  # URL постера
                "shortDescription": film["shortDescription"] or "",  # Краткое описание
                "reviews": film["reviews"],  # Обзоры (текст)
                "review_vector": review_vector  # Векторное представление обзоров
            }
        )
    print('Индексация прошла успешно!')


if __name__ == "__main__":
    app.app_context().push()
    films_data = get_films()

    index_films(films_data)

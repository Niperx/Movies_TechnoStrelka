from app.models import Film, Review
from app import app, db, model
import sqlalchemy as sa
import sqlalchemy.orm as so

from search import es

# from sentence_transformers import SentenceTransformer

# Загрузка модели
# model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_films_with_reviews():
    # Получаем все фильмы
    films = db.session.scalars(
        sa.select(Film).options(so.subqueryload(Film.review))
    ).all()

    # Формируем данные для индексации
    films_data = []
    for film in films:
        # Извлекаем тексты обзоров
        reviews = [review.text for review in film.review]

        # Объединяем обзоры в одну строку
        reviews_text = " ".join(reviews)

        # Формируем словарь с данными фильма
        film_data = {
            "id": film.id,
            "title": film.title,
            "genres": film.genres,
            "description": film.description,
            "ai_moment": film.ai_moment,
            # "reviews": reviews_text,  # Объединённые обзоры
            "poster_Url": film.poster_Url
        }
        films_data.append(film_data)

    return films_data


# Функция для индексации фильмов
def index_films(films):
    for film in films:
        # Генерация векторов для каждого текстового поля
        description_vector = model.encode(film["description"] or "").tolist()
        # review_vector = model.encode(" ".join(film["reviews"]) if film["reviews"] else "").tolist()  # Объединяем рецензии
        ai_moment_vector = model.encode(film["ai_moment"] or "").tolist()  # Используем ai_moment

        # Индексация фильма в Elasticsearch
        es.index(
            index="films",
            id=film["id"],  # Используем ID фильма
            document={
                "title": film["title"],
                "genres": film["genres"],
                "description": film["description"] or "",
                "description_vector": description_vector,
                # "reviews": film["reviews"] or [],
                # "review_vector": review_vector,
                "ai_moment": film["ai_moment"] or "",
                "ai_moment_vector": ai_moment_vector,
                "poster_Url": film["poster_Url"] or ""  # Добавляем URL постера
            }
        )


if __name__ == "__main__":
    app.app_context().push()
    data = get_films_with_reviews()
    index_films(data)



    # Преобразование текста в вектор
    # text = "Это тестовый текст."
    # vector = model.encode(text)
    #
    # print(vector)  # Выведет числовой вектор
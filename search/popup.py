from app.models import Film
from app import app

from search import es
from elasticsearch.helpers import bulk

def index_films():
    films = Film.query.all()  # Получаем все фильмы из базы данных
    actions = []
    for film in films:
        # Формируем документ для Elasticsearch
        doc = {
            "_index": "films",  # Название индекса
            "_id": film.id,     # ID фильма
            "title": film.title,
            "description": film.description or "",
            "tags": [tag.name for tag in film.tags],  # Список тегов
            "poster_Url": film.poster_Url,
            "ai_moment": film.ai_moment,
            "genres": film.genres,
            "reviews": [review.text for review in film.review]  # Список рецензий
        }
        print(doc)
        actions.append(doc)

    # Массовая загрузка данных в Elasticsearch

    bulk(es, actions)
    print(f"Indexed {len(actions)} films.")


if __name__ == "__main__":
    app.app_context().push()
    index_films()
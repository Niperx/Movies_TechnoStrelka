from app.models import Film, Tag
from app import db, app

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
            "poster_Url": film.poster_Url
        }
        print(doc)
        actions.append(doc)

    # Массовая загрузка данных в Elasticsearch
    from elasticsearch import Elasticsearch
    es = Elasticsearch("http://localhost:9200")  # Подключение к Elasticsearch
    bulk(es, actions)
    print(f"Indexed {len(actions)} films.")


app.app_context().push()
# Вызовите функцию для индексации
index_films()
# main.py
from time import sleep

import requests
import sqlalchemy as sa
from app.models import Film, Tag
from app import db, app
from ai import ai_to_tags

# Замените 'YOUR_API_KEY' на ваш реальный API-ключ
API_KEY = '182f0379-d2e4-4674-a955-fc69e26f4ded'


def get_film(id):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY,
    }

    url = f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{id}'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем статус ответа

        data = response.json()
        return data


    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []


def get_top_films(top_type, page):
    """
    Функция для получения топ-250 фильмов.
    :param top_type: Тип топа ('TOP_250_BEST_FILMS' или 'TOP_100_POPULAR_FILMS').
    :param page: Номер страницы (по умолчанию 1).
    :return: Список фильмов из топа.
    """
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY,
    }

    params = {
        'type': top_type,
        'page': page
    }

    url = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/top'

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Проверяем статус ответа

        data = response.json()
        sleep(2)
        print(data)
        mvs = data.get('films', [])
        movies = []
        for film in mvs:
            id = film['filmId']
            mv = get_film(id)
            movies.append(mv)

        if not mvs:
            print("Фильмы не найдены.")
            return []

        return movies

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []


def save_films_to_database(films):
    """
    Сохраняет фильмы в базу данных через SQLAlchemy.
    :param films: Список фильмов для сохранения.
    """
    app.app_context().push()
    for film in films:
        print(film)
        # Проверяем, существует ли фильм с таким film_id в базе данных
        # existing_film = session.query(Film).filter_by(film_id=film['filmId']).first()

        existing_film = db.session.scalar(sa.select(Film).where(Film.film_id == film['kinopoiskId']))
        if not existing_film:
            tags = ai_to_tags(film['nameRu'])
            film_tags = []
            for t in tags:
                existing_tag = db.session.scalar(sa.select(Tag).where(Tag.name == t))
                if not existing_tag:
                    new_tag = Tag(
                        name=t
                    )
                    db.session.add(new_tag)
                    film_tags.append(new_tag)
                else:
                    film_tags.append(existing_tag)
            db.session.commit()
            gens = ', '.join([gen['genre'] for gen in film.get('genres', [])])
            cont = ', '.join([con['country'] for con in film.get('countries', [])])
            new_film = Film(
                film_id=film['kinopoiskId'],
                title=film['nameRu'],
                year=film['year'],
                rating=film.get('ratingKinopoisk'),
                description=film.get('description'),
                shortDescription=film.get('shortDescription'),
                poster_Url=film.get('posterUrl'),
                poster_Url_preview=film.get('posterUrlPreview'),
                cover_Url=film.get('coverUrl'),
                wed_Url=film.get('webUrl'),
                genres=gens,
                countries=cont,
                tags=film_tags
            )

            db.session.add(new_film)
            db.session.commit()
            print(f'Добавлен -- {film['nameRu']}')
        else:
            print(f"Фильм с ID {film['kinopoiskId']} уже существует в базе данных.")




# Пример использования функций
if __name__ == "__main__":
    for i in range(1, 2):
        films = get_top_films(top_type='TOP_250_BEST_FILMS', page=i)
        save_films_to_database(films)
        print(f"Страница {i} готова!")
        sleep(1)
    # Получаем топ-250 фильмов

    # films = get_top_films(top_type='TOP_250_BEST_FILMS', page=2)
    # save_films_to_database(films)
    # sleep(2)
    # films = get_top_films(top_type='TOP_250_BEST_FILMS', page=3)
    # save_films_to_database(films)

    print("Готово!")
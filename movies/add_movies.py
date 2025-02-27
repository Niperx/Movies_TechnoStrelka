from time import sleep
import requests
import sqlalchemy as sa
from app.models import Film, Tag, Review
from app import db, app
from ai import ai_to_tags, ai_moment

from movies import Config


def get_film(id):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': Config.kp_API_KEY,
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


def get_films_by_page(page=1):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': Config.kp_API_KEY,
    }
    url = "https://kinopoiskapiunofficial.tech/api/v2.2/films"
    params = {
        "genres": 7,
        "order": "RATING",
        "type": "FILM",
        "ratingFrom": 0,
        "ratingTo": 10,
        "yearFrom": 2000,
        "yearTo": 2024,
        "page": page
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        sleep(2)
        print(data)
        mvs = data.get('items', [])

        if not mvs:
            print("Фильмы не найдены.")
            return []

        movies = []
        for film in mvs:
            id = film['kinopoiskId']
            if film['nameRu']:
                mv = get_film(id)
                movies.append(mv)

        return movies

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []


def get_top_films(top_type, page):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': Config.kp_API_KEY,
    }

    params = {
        'type': top_type,
        'page': page
    }

    url = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/top'

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        sleep(2)
        print(data)
        mvs = data.get('films', [])

        if not mvs:
            print("Фильмы не найдены.")
            return []

        movies = []
        for film in mvs:
            id = film['filmId']
            mv = get_film(id)
            movies.append(mv)

        return movies

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []


def get_review(id):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': Config.kp_API_KEY,
    }

    params = {
        'page': 1
    }

    url = f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{id}/reviews'

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Проверяем статус ответа

        data = response.json()
        return data.get('items')


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
        existing_film = db.session.scalar(sa.select(Film).where(Film.film_id == film['kinopoiskId']))
        if not existing_film:
            ai_moments = ai_moment(f"{film['nameRu']} ({film['year']})")
            tags = ai_to_tags(f"{film['nameRu']} ({film['year']})")
            reviews = get_review(film['kinopoiskId'])

            film_tags = []
            # Добавляем теги
            for t in tags:
                existing_tag = db.session.scalar(sa.select(Tag).where(Tag.name == t))
                if not existing_tag:
                    existing_tag = Tag(name=t)
                    db.session.add(existing_tag)
                film_tags.append(existing_tag)

            # Добавляем отзывы
            film_reviews = []
            for rew in reviews:
                if rew['type'] == 'POSITIVE':
                    existing_review = db.session.scalar(sa.select(Review).where(Review.text == rew['description']))
                    if not existing_review:
                        existing_review = Review(text=rew['description'])
                        db.session.add(existing_review)
                    film_reviews.append(existing_review)

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
                ai_moment=ai_moments
            )

            db.session.add(new_film)
            db.session.commit()

            # Добавляем связи между фильмом и тегами через ORM
            for tag in film_tags:
                if tag not in new_film.tags:
                    new_film.tags.append(tag)

            # Добавляем связи между фильмом и отзывами через ORM
            for review in film_reviews:
                if review not in new_film.review:
                    new_film.review.append(review)

            db.session.commit()
            print(f'Добавлен -- {film['nameRu']}')
        else:
            print(f"Фильм с ID {film['kinopoiskId']} уже существует в базе данных.")


if __name__ == "__main__":
    # for i in range(13, 14):
    #     films = get_top_films(top_type='TOP_250_BEST_FILMS', page=i)
    #     save_films_to_database(films)
    #     print(f"Страница {i} готова!")
    #     sleep(1)
    for i in range(4, 6):
        films = get_films_by_page(page=i)
        save_films_to_database(films)
        print(f"Страница {i} готова!")
        sleep(1)
    # # Пример использования
    # all_films = get_films_by_page(1)
    # print(all_films)
    # print(get_review(535341).get('items')[2])
    # for rew in get_review(535341).get('items'):
    #     if rew['type'] == 'POSITIVE':
    #         print(rew['description'])
    # Получаем топ-250 фильмов
    print("Готово!")
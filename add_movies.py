# main.py
from time import sleep

import requests
import sqlalchemy as sa
from app.models import Film # Импортируем модель и Base из models.py
from app import db, app

# Замените 'YOUR_API_KEY' на ваш реальный API-ключ
API_KEY = '862e6c17-39b9-4bba-873a-4ffa03edb9cb'
BASE_URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/top'


def get_film(id):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY,
    }

    params = {
        'id': id
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


def get_top_films(top_type='TOP_250_BEST_FILMS', page=1):
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

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()  # Проверяем статус ответа

        data = response.json()
        print(data)
        films = data.get('films', [])
        movies = []
        for film in films:
            id = film['filmId']
            mv = get_film(id)
            movies.append(mv)

        print(movies)



        if not films:
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
        print(f'ЧТО ЭТО {existing_film}')
        if not existing_film:
            gens = ''
            for gen in film['genres']:
                gens += gen['genre'] + ', '
            cont = ''
            for con in film['countries']:
                cont += con['country'] + ', '
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
                countries=cont
            )
            db.session.add(new_film)
            print(f'Добавлен -- {film['nameRu']}')
        else:
            print(f"Фильм с ID {film['kinopoiskId']} уже существует в базе данных.")

    db.session.commit()


# Пример использования функций
if __name__ == "__main__":
    # Получаем топ-250 фильмов
    films = get_top_films(top_type='TOP_250_BEST_FILMS', page=1)
    save_films_to_database(films)
    sleep(1)
    films = get_top_films(top_type='TOP_250_BEST_FILMS', page=2)
    save_films_to_database(films)
    sleep(1)
    films = get_top_films(top_type='TOP_250_BEST_FILMS', page=3)
    save_films_to_database(films)

    print("Готово!")
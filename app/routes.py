from datetime import datetime, timezone
import numpy as np
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import app, db, model
from app.models import User, Film, Tag, Rating, Comment, SearchHistory
from app.forms import LoginForm, RegistrationForm, EditProfileForm, RatingForm, CommentForm
from search import es

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/')
def index():
    # Получаем номер страницы из параметров запроса (по умолчанию 1)
    page = request.args.get('page', 1, type=int)
    per_page = 24  # Количество фильмов на странице

    # Параметр сортировки (по умолчанию 'id')
    sort_by = request.args.get('sort_by', 'id')  # Может быть 'id', 'rating', или 'year'

    # Определяем поле для сортировки
    if sort_by == 'rating':
        order_by = Film.rating.desc()  # Сортировка по рейтингу (по убыванию)
    elif sort_by == 'year':
        order_by = Film.year.desc()  # Сортировка по году (по убыванию)
    else:
        order_by = Film.id.asc()  # Сортировка по ID (по возрастанию)

    # Пагинация фильмов с учетом сортировки
    pagination = Film.query.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)
    films = pagination.items  # Фильмы текущей страницы

    return render_template('index.html', films=films, pagination=pagination, sort_by=sort_by)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Войти', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, вы успешно зарегистрировались!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    comments = user.comments.order_by(Comment.timestamp.desc()).all()
    return render_template('user.html', user=user, comments=comments)


@app.route('/movie/<film_id>', methods=['GET', 'POST'])
def movie(film_id):
    film = Film.query.get_or_404(film_id)
    rating_form = RatingForm()
    comment_form = CommentForm()

    # Проверяем, является ли запрос AJAX
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Обработка формы оценки
        if rating_form.validate_on_submit():
            score = rating_form.score.data
            existing_rating = Rating.query.filter_by(user_id=current_user.id, film_id=film.id).first()
            if existing_rating:
                existing_rating.score = score
            else:
                new_rating = Rating(score=score, user=current_user, film=film)
                db.session.add(new_rating)
            db.session.commit()
            return jsonify(success=True, message="Ваша оценка сохранена!")

        # Обработка формы комментария
        elif comment_form.validate_on_submit():
            text = comment_form.text.data
            new_comment = Comment(text=text, user=current_user, film=film)
            db.session.add(new_comment)
            db.session.commit()
            return jsonify(success=True, message="Ваш комментарий добавлен!")

        # Если форма не прошла валидацию
        return jsonify(success=False, message="Ошибка при сохранении данных.")

    # Загрузка оценок и комментариев
    ratings = film.ratings.all()
    average_rating = round(sum(r.score for r in ratings) / len(ratings), 1) if ratings else None
    comments = film.comments.order_by(Comment.timestamp.desc()).all()

    return render_template(
        'movie.html',
        movie=film,
        rating_form=rating_form,
        comment_form=comment_form,
        average_rating=average_rating,
        comments=comments
    )


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Ваши данные были внесены и сохранены')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактирование профиля',
                           form=form)



@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip().lower()
    if not query:
        return render_template('search_results.html', films=[], query=query)

    try:
        # Проверяем, является ли запрос жанром
        genres = ['драма', 'комедия', 'фантастика', 'приключения', 'триллер', 'детектив', 'криминал', 'фэнтези', 'боевик',
             'мелодрама', 'военный', 'история', 'мультфильм', 'семейный', 'аниме', 'биография', 'музыка', 'спорт', 'мюзикл',
             'вестерн', 'ужасы', 'детский', 'документальный', 'короткометражка']
        is_genre_query = any(genre in query for genre in genres)

        if is_genre_query:
            # Фильтрация по жанру
            response = es.search(
                index="films",
                body={
                    "query": {
                        "bool": {
                            "filter": [
                                {"terms": {"genres": [query]}}  # Фильтр по жанру
                            ]
                        }
                    },
                    "size": 6  # Ограничение количества результатов
                }
            )
        else:
            # Преобразуем запрос в вектор
            query_vector = model.encode(query).tolist()

            # Комбинированный поиск: по названию, смыслу и обзорам
            response = es.search(
                index="films",
                body={
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "match_phrase": {
                                        "title": {
                                            "query": query,
                                            "boost": 3.0  # Увеличиваем приоритет фразового поиска
                                        }
                                    }
                                },
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["title^4", "description", "ai_moment"],
                                        "operator": "and",  # Требуем совпадение всех слов
                                        "fuzziness": "AUTO"
                                    }
                                },
                                {
                                    "script_score": {
                                        "query": {"match_all": {}},
                                        "script": {
                                            "source": "cosineSimilarity(params.query_vector, 'description_vector') * 2.0 + 1.0",
                                            "params": {"query_vector": query_vector}
                                        }
                                    }
                                },
                                {
                                    "script_score": {
                                        "query": {"match_all": {}},
                                        "script": {
                                            "source": "cosineSimilarity(params.query_vector, 'ai_moment_vector') * 1.5 + 1.0",
                                            "params": {"query_vector": query_vector}
                                        }
                                    }
                                },
                                {
                                    "script_score": {
                                        "query": {"match_all": {}},
                                        "script": {
                                            "source": "cosineSimilarity(params.query_vector, 'review_vector') * 1.0 + 1.0",
                                            "params": {"query_vector": query_vector}
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "min_score": 3.5,  # Минимальная оценка релевантности
                    "size": 6          # Ограничение количества результатов
                }
            )

        # Извлекаем найденные фильмы
        films = []
        for hit in response["hits"]["hits"]:
            film_data = hit["_source"]
            film_data["id"] = hit["_id"]
            film_data["score"] = hit["_score"]  # Добавляем релевантность
            films.append(film_data)

        if current_user.is_authenticated:
            search_entry = SearchHistory(user_id=current_user.id, query=query)
            db.session.add(search_entry)
            db.session.commit()

        return render_template('search_results.html', films=films, query=query)

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return render_template('search_results.html', films=[], query=query, error=str(e))


def get_recommendations(top_n=6):
    # Получаем историю поиска пользователя
    history = db.session.query(SearchHistory).filter_by(user_id=current_user.id).order_by(
        SearchHistory.timestamp.desc()).limit(3).all()

    if not history:
        return []

    # Собираем уникальные запросы пользователя
    queries = list(set(entry.query for entry in history))


    # Преобразуем запросы в векторы
    query_vectors = [model.encode(query).tolist() for query in queries]


    # Находим средний вектор для всех запросов
    avg_vector = np.mean(query_vectors, axis=0).tolist()


    # Ищем фильмы, схожие со средним вектором
    response = es.search(
        index="films",
        body={
            "query": {
                "function_score": {
                    "query": {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.avg_vector, 'ai_moment_vector') + 1.0",
                                "params": {"avg_vector": avg_vector}
                            }
                        }
                    },
                    # "random_score": {},  # Добавляем случайность
                    # "boost_mode": "sum"
                }
            },
            "min_score": 1,  # Уменьшаем порог
            "size": top_n  # Количество рекомендаций
        }
    )

    # Извлекаем рекомендованные фильмы
    recommendations = []
    for hit in response["hits"]["hits"]:
        film_data = hit["_source"]
        film_data["id"] = hit["_id"]
        film_data["score"] = hit["_score"]
        recommendations.append(film_data)

    # print("Рекомендации:", recommendations)
    return recommendations


@app.route('/for_you')
@login_required  # Только для авторизованных пользователей
def for_you():
    # Получаем рекомендации для текущего пользователя
    recommendations = get_recommendations()

    return render_template('for_you.html', recommendations=recommendations)
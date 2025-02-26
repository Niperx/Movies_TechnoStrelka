from datetime import datetime, timezone
# from sentence_transformers import SentenceTransformer
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import app, db, model
from app.models import User, Film, Tag, Rating, Comment
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

    # Пагинация фильмов
    pagination = Film.query.paginate(page=page, per_page=per_page, error_out=False)
    films = pagination.items  # Фильмы текущей страницы

    return render_template('index.html', films=films, pagination=pagination)


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
    return render_template('user.html', user=user)


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
    # Получаем запрос от пользователя
    query = request.args.get('query', '').strip().lower()
    if not query:
        return render_template('search_results.html', films=[], query=query)

    try:
        # Преобразуем запрос в вектор
        # model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        query_vector = model.encode(query).tolist()

        # Проверяем, существует ли индекс
        if not es.indices.exists(index="films"):
            return render_template('search_results.html', films=[], query=query, error="Индекс 'films' не существует.")

        # Поиск в Elasticsearch
        response = es.search(
            index="films",
            body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^3", "description^2", "ai_moment", "genres"],
                                    "type": "best_fields",
                                    "minimum_should_match": "75%",
                                    "fuzziness": "AUTO"
                                }
                            },
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'description_vector') + 1.0",
                                        "params": {"query_vector": query_vector}
                                    }
                                }
                            },
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'ai_moment_vector') + 1.0",
                                        "params": {"query_vector": query_vector}
                                    }
                                }
                            }
                            # {
                            #     "script_score": {
                            #         "query": {"match_all": {}},
                            #         "script": {
                            #             "source": "cosineSimilarity(params.query_vector, 'review_vector') + 0.8",
                            #             "params": {"query_vector": query_vector}
                            #         }
                            #     }
                            # }
                        ]
                    }
                },
                "min_score": 10,
                "size": 20
            }
        )

        # Извлекаем найденные фильмы
        films = []
        for hit in response["hits"]["hits"]:
            film_data = hit["_source"]
            film_data["id"] = hit["_id"]  # Извлекаем ID фильма
            film_data["score"] = hit["_score"]  # Добавляем релевантность
            films.append(film_data)

        return render_template('search_results.html', films=films, query=query)

    except Exception as e:
        # Обработка ошибок
        print(f"Ошибка при выполнении запроса: {e}")
        return render_template('search_results.html', films=[], query=query, error=str(e))
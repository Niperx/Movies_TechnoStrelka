from search import create_vector, create_index
from app import app

if __name__ == "__main__":
    create_index.create_index('films')

    app.app_context().push()
    films_data = create_vector.get_films()

    create_vector.index_films(films_data)
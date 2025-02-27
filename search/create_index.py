from search import es, index_settings

if es.ping():
    print("Подключение успешно!")
else:
    print("Не удалось подключиться.")

# Создание индекса
def create_index(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(
            index=index_name,
            body=index_settings
        )
        print(es.indices.exists(index=index_name))
        print(f'"{index_name}" создан!')
    else:
        print(f'"{index_name}" уже существует!')

if __name__ == "__main__":
    create_index('films')
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
        # new_index_name = f"{index_name}_updated"
        # es.indices.create(index=new_index_name, body=index_settings)
        # query = {"query": {"match_all": {}}}
        # es.reindex(body={"source": {"index": index_name}, "dest": {"index": new_index_name}})
        # # Удаляем старый индекс
        # es.indices.delete(index=index_name)
        #
        # # Переименовываем новый индекс обратно
        # es.indices.put_alias(index=new_index_name, name=index_name)
        # es.indices.delete(index=new_index_name)
        # print(f'"{index_name}" обновлён!')
        print(f'"{index_name}" уже существует!')

if __name__ == "__main__":
    create_index('films')
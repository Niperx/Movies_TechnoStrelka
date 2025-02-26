from search import es

# Удаление индекса "films"
def delete_index(index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Индекс '{index_name}' удален.")
    else:
        print(f"Индекс '{index_name}' не существует.")

if __name__ == "__main__":
    delete_index("films")
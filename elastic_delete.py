from elasticsearch import Elasticsearch

# Подключение к Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Удаление индекса "films"
index_name = "films"
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f"Индекс '{index_name}' удален.")
else:
    print(f"Индекс '{index_name}' не существует.")
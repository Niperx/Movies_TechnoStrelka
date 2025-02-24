from elasticsearch import Elasticsearch

# Подключение к Elasticsearch
es = Elasticsearch("http://localhost:9200")

if es.ping():
    print("Подключение успешно!")
else:
    print("Не удалось подключиться.")

# Создание индекса
index_name = "films"
if not es.indices.exists(index=index_name):
    es.indices.create(
        index=index_name,
        body={
            "settings": {
                "analysis": {
                    "analyzer": {
                        "russian_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                        }
                    },
                    "filter": {
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "title": {"type": "text", "analyzer": "russian_analyzer"},
                    "description": {"type": "text", "analyzer": "russian_analyzer"},
                    "tags": {"type": "text", "analyzer": "russian_analyzer"}
                }
            }
        }
    )
    print(es.indices.exists(index=index_name))
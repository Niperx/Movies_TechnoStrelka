from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "refresh_interval": "30s"  # Увеличиваем интервал обновления индекса
    },
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "description": {"type": "text"},
            "description_vector": {
                "type": "dense_vector",
                "dims": 384  # Размерность вектора (зависит от модели)
            },
            "genres": {"type": "keyword"},  # Для фильтрации жанров
            "ai_moment": {"type": "text"},
            "ai_moment_vector": {
                "type": "dense_vector",
                "dims": 384
            },
            "poster_Url": {"type": "keyword"},  # Поле для URL постера
            "shortDescription": {"type": "text"},  # Краткое описание (не используется в поиске)
            "reviews": {"type": "text"},  # Обзоры (текст)
            "review_vector": {
                "type": "dense_vector",
                "dims": 384  # Векторное представление обзоров
            }
        }
    }
}


### Система тегов
# index_settings = {
#     "settings": {
#         "analysis": {
#             "analyzer": {
#                 "russian_analyzer": {
#                     "type": "custom",
#                     "tokenizer": "standard",
#                     "filter": ["lowercase", "russian_stop", "russian_stemmer"]
#                 }
#             },
#             "filter": {
#                 "russian_stop": {
#                     "type": "stop",
#                     "stopwords": ["_russian_"]
#                 },
#                 "russian_stemmer": {
#                     "type": "stemmer",
#                     "language": "russian"
#                 }
#             }
#         }
#     },
#     "mappings": {
#         "properties": {
#             "title": {"type": "text", "analyzer": "russian_analyzer"},
#             "description": {"type": "text", "analyzer": "russian_analyzer"},
#             "tags": {"type": "text", "analyzer": "russian_analyzer"},
#             "ai_moments": {"type": "text", "analyzer": "russian_analyzer"},
#             "genres": {"type": "text", "analyzer": "russian_analyzer"},
#             "review": {  # Добавляем поле для рецензий
#                 "properties": {
#                     "text": {"type": "text", "analyzer": "russian_analyzer"}
#                 }
#             }
#         }
#     }
# }

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


index_settings = {
    "settings": {
        "number_of_shards": 1,  # Один шард для небольших данных
        "number_of_replicas": 0,  # Отключаем реплики для уменьшения нагрузки
        "refresh_interval": "30s"  # Увеличиваем интервал обновления индекса
    },
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "genres": {"type": "text"},
            "description": {"type": "text"},
            "description_vector": {
                "type": "dense_vector",
                "dims": 384
            },
            # "reviews": {"type": "text"},
            # "review_vector": {
            #     "type": "dense_vector",
            #     "dims": 384
            # },
            "ai_moment": {"type": "text"},
            "ai_moment_vector": {
                "type": "dense_vector",
                "dims": 384
            },
            "poster_Url": {"type": "keyword"}  # Поле для URL постера
        }
    }
}



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

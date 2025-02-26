## [*Terminal*]
### Запуск проекта

Создаём окружение
```
python -m venv venv
```
Активируем окружение
```
venv\Scripts\Activate.ps1
```
Устанавливаем нужные библиотеки
```
pip install -r requirements.txt
```
Настройка проекта
```
set FLASK_APP=main.py
```
Запуск
```
flask run
```
> [!NOTE]
> Убедитесь что сервер для обработки поиска запущен

### Запуск поиск-сервиса

1. Скачать ElasticSearch
2. Запустить сервис через Bash ```./bin/elasticsearch```
> [!TIP]
> Сервис будет доступен по адресу: http://localhost:9200
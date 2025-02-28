<p align="center">
  <img src="https://i.ibb.co/MkHwcFYS/cute-black-cat-in-glasses-black-wallpaper.jpg" alt="CatiWeb Team"/>
</p>

## Дополнительные файлы перед запуском проекта
1. ~~База с фильмами main.db - [Yandex Disk](https://disk.yandex.ru/d/8iWYkXAFsiRfJA) (поместить в папку db в проекте)~~
>Уже присутствует в репозитории (76mb)
2. ElasticSearch - [Yandex Disk](https://disk.yandex.ru/d/NnZI88rn5qWgbw) (разместить в любом удобном месте)
>Заменить файл по пути "ElasticSearch/config/elasticsearch.yml" - [Yandex Disk](https://disk.yandex.ru/d/UQCRDshumdIVaA)

## Запуск поиск-сервиса

1. Скачать ElasticSearch
2. Запустить сервис через Bash ```./bin/elasticsearch```
> [!TIP]
> Сервис будет доступен по адресу: http://localhost:9200

> [!NOTE]
> На время проверки проекта, можно отключить https протокол в файле по пути```/config/elasticsearch.yml```, либо заменить файл на тот, что можно скачать выше

## Настройка проекта
1. Устанавливаем проект в ручную или через git
```
git clone https://github.com/Niperx/Movies_TechnoStrelka.git
```
2. Создаём окружение в папке с проектом
```
python -m venv venv
```
3. Активируем окружение
```
venv\Scripts\Activate.ps1
```
4. Устанавливаем нужные библиотеки
```
pip install -r requirements.txt
```
5. Запускаем файл настройки и обучения поиска по существующей базе фильмов
```
python setup.py
```
> [!TIP]
> Это может занять какое-то время, пока скачается модель и проиндексируется вся база с фильмами
> 
6. Устанавливаем файл запуска для Flask
```
set FLASK_APP=main.py
```
## Запуск
```
flask run
```
> [!NOTE]
> Убедитесь что сервер для обработки поиска запущен и база фильмов проиндексирована

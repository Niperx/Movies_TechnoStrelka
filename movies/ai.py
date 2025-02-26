from time import sleep

import sqlalchemy as sa
from app.models import Film # Импортируем модель и Base из models.py
from app import db, app

from openai import OpenAI

# Proxy
client = OpenAI(
    api_key="sk-MsYz8DlX7XHgtxT4fifxj3RVfvUWOb1D",
    base_url="https://api.proxyapi.ru/openai/v1",
)

def get_custom_response(prompt, role=''):
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": role},
            {"role": "user",
             "content": prompt}
        ]
    )
    return chat_completion.choices[0].message.content


# OpenRouter
# client = OpenAI(
#     api_key="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",
#     base_url="https://openrouter.ai/api/v1",
# )
#
# def get_custom_response(prompt, role=''):
#     chat_completion = client.chat.completions.create(
#         model="qwen/qwen2.5-vl-72b-instruct:free",
#         messages=[
#             {"role": "system",
#              "content": role},
#             {"role": "user",
#              "content": prompt}
#         ]
#     )
#     print(chat_completion)
#     return chat_completion.choices[0].message.content

app.app_context().push()

def ai_to_tags(title):
    print(title)
    ai_answer = get_custom_response(
        f'{title}',
        'Ты эксперт по фильмам, который отвечает от 5-ти до 10-ти простыми тегами на название фильма и его смысл, которое напишет пользователь. Отвечай без "#", "." и других символов, просто перечисляя их через запятую!'
    )
    good_tags = []
    if ai_answer[-1] == '.':
        ai_answer = ai_answer[:-1]
    tags_to_sp = ai_answer.split(', ')
    for tag in tags_to_sp:
        tag = tag.lower()
        if ' ' in tag:
            tag = tag.replace(' ', '')
            tag = tag.replace('.', '')
            tag = tag.replace('!', '')
            tag = tag.replace('?', '')
        good_tags.append(tag)


    return good_tags

def ai_moment(title, year=''):
    ai_answer = get_custom_response(
        f'{title} {year}',
        'Ты эксперт по фильмам, который подробно пересказывает самые основные, яркие и запоминающиеся моменты из фильма, '
        'название которого напишет пользователь. '
        'Отвечай текстом до 5000 символов считая знаки препинания'
    )
    return ai_answer


def save_tags(num, text):
    info = db.session.scalar(
        sa.select(Film).where(Film.id == num)
    )

    info.tags = text
    db.session.commit()

def save_moment(num, text):
    info = db.session.scalar(
        sa.select(Film).where(Film.id == num)
    )

    info.ai_moment = text
    db.session.commit()

if __name__ == "__main__":
    for i in range(11, 60):
        mv = db.session.scalar(
            sa.select(Film).where(Film.id == i)
        )
        moment = ai_moment(mv.title, f'({mv.year})')
        save_moment(i, moment)
        print(moment)
        print(f'{mv.title} - моменты добавлены')
        sleep(1)




# print(get_custom_response('Сумерки', 'Ты эксперт по фильмам, который отвечает 10-ью простыми тегами на название фильма, которое напишет пользователь'))
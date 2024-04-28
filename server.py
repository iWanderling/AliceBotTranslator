from flask import Flask, request, jsonify
from translate import Translator
import logging


translator = Translator(from_lang='ru', to_lang="en")
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают непосредственно за ведение диалога:
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'animal': 'Слона'
        }

        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    for satisfy in ['ладно', 'куплю', 'покупаю', 'хорошо']:
        if satisfy in req['request']['original_utterance'].lower():
            if sessionStorage[user_id]['animal'] == 'Слона':
                # Пользователь согласился, прощаемся.
                res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
                sessionStorage[user_id]['animal'] = 'Кролика'
            else:
                res['response']['text'] = 'Кролика можно найти на Яндекс.Маркете!'
                res['response']['end_session'] = True
                return

    # Если нет, то убеждаем его купить слона / кролика!
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {sessionStorage[user_id]['animal']}!"
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={sessionStorage[user_id]['animal']}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
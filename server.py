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
    if req['session']['new']:
        res['response']['text'] = 'Я умею переводить текст с русского на английский!'
        return

    parse = req['request']['original_utterance'].split()
    if 'переведи' in parse[0].lower() and 'слово' in parse[1].lower():
        res['response']['text'] = \
            f"'{translator.translate(' '.join(parse[2:]))}"
    else:
        res['response']['text'] = 'Отправьте запрос следующего формата: "Переведи(-те) слово [слово | предложение]".'


if __name__ == '__main__':
    app.run()

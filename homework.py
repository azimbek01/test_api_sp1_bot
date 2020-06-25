import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(TELEGRAM_TOKEN)

URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise RuntimeError('Имя задания неопределено - None')
    else:
        if homework.get('status') is None:
            raise RuntimeError(
                f'Неопределенный статус у задания {homework_name}'
            )
        else:
            if homework['status'] == 'rejected':
                verdict = 'К сожалению в работе нашлись ошибки.'
            elif homework['status'] == 'approved':
                verdict = 'Ревьюеру всё понравилось, можно ' \
                           'приступать к следующему уроку.'
            else:
                raise RuntimeError(
                    f'Неизвестный статус у задания {homework_name}'
                )

            return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {
        'Authorization': f'OAuth {PRACTICUM_TOKEN}'
    }
    if current_timestamp is None:
        current_timestamp = int(time.time())
    data = {
        'from_date': current_timestamp
    }

    try:
        homework_statuses = requests.get(URL, headers=headers, params=data)
        return homework_statuses.json()
    except Exception as e:
        print(f'Ошибка подключения к сайту: {e}')


def send_message(message):
    return bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                    )
            current_timestamp = new_homework.get('current_date')
            time.sleep(900)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
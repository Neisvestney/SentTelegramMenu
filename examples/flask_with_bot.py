import logging
import os
from threading import Thread

import telebot

from tmenu import TelegramMenu

from flask import Flask
from flask import request

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


class Database:
    temp = 0

    def temp_validation(self, temp):
        if temp.isnumeric():
            return None, int(temp)
        else:
            return "Temp mast be a number!", None


bot = TelegramMenu(os.environ.get("TELEGRAM_TOKEN"), lambda chat_id, user: {
    'main': {
        'text': f'Flask example',
        'buttons': {
            'set_button': {
                'button': 'Set temp',
                'input': {
                    'text': 'Enter temp: ',
                    'db_field': 'temp'
                }
            },
            'get_button': {
                'button': 'Get temp',
                'notification': f'Temp: {bot.database.temp}'
            },
        }
    }
}, database_class=Database)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_menu(message.chat.id, ['main'])


app = Flask(__name__)


@app.route('/')  # url example 'http://127.0.0.1:5000/?temp=123'
def set_temp():
    bot.database.temp = int(request.args.get('temp')) if request.args.get('temp').isnumeric() else None
    return 'OK'


process = Thread(target=lambda: app.run())
process.start()


bot.polling()

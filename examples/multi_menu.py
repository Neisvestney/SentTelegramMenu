import logging
import os

import telebot

from tmenu import TelegramMenu

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = TelegramMenu(os.environ.get("TELEGRAM_TOKEN"), lambda message, user: {
    'main': {
        'text': 'Menu 1',
        'buttons': {
            'send_notification': {
                'button': 'Send Notification',
                'notification': "Test Notification"
            }
        }
    },
    'two': {
        'text': 'Menu 2',
        'buttons': {
            'function_button': {
                'button': 'Print in terminal',
                'func': lambda m, u: print(m.chat.id)
            }
        }
    }
})


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Password: ')


@bot.message_handler(func=lambda message: bot.get_user(message.chat.id).step is None)
def get_password(message):
    if message.text == 'Test':
        bot.get_user(message.chat.id).step = 'password'
        bot.send_message(message.chat.id, 'Select menu:\n/main\n/two')
    else:
        bot.send_message(message.chat.id, 'Password: ')


@bot.message_handler(commands=['main'], func=lambda message: bot.get_user(message.chat.id).step is not None)
def select(message):
    bot.send_menu(message.chat.id, ['main'])


@bot.message_handler(commands=['two'], func=lambda message: bot.get_user(message.chat.id).step is not None)
def select(message):
    bot.send_menu(message.chat.id, ['two'])


bot.polling()

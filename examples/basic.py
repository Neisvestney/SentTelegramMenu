import logging
import os

import telebot

from tmenu import TelegramMenu

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = TelegramMenu(os.environ.get("TELEGRAM_TOKEN"), lambda message, user: {
    'main': {
        'text': 'Basic usage',
        'buttons': {
            'test': {
                'text': 'You in submenu',
                'button': 'Submenu',
                'buttons': {'back': {'button': 'Back'}}
            },
            'send_notification': {
                'button': 'Send Notification',
                'notification': "Test Notification"
            },
            'function_button': {
                'button': 'Print in terminal',
                'func': lambda m, u: print(m.chat.id)
            }
        }
    }
})


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_menu(message.chat.id, ['main'])


bot.polling()

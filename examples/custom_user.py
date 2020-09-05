import logging
import os

import telebot

from tmenu import TelegramMenu, TelegramUser

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


class CustomUser(TelegramUser):
    name = None
    age = 0

    def age_validation(self, age):
        if age.isnumeric():
            return None, int(age)
        else:
            return "Age mast be a number!", None


bot = TelegramMenu(os.environ.get("TELEGRAM_TOKEN"), lambda chat_id, user: {
    'main': {
        'text': f'Custom user\nYou name: {user.name}\nYou age: {user.age}',
        'buttons': {
            'name_button': {
                'button': 'Set name',
                'input': {
                    'text': 'Enter your name: ',
                    'field': 'name'
                }
            },
            'age_button': {
                'button': 'Set age',
                'input': {
                    'text': 'Enter your age: ',
                    'field': 'age'
                }
            },
            'other': {
                'button': 'Other',
                'text': 'Other',
                'buttons': {
                    'print_button': {
                        'button': 'Print in console',
                        'input': {
                            'text': 'Enter text: ',
                            'func': lambda t: print(t)
                        }
                    },
                    'back': {'button': 'Back'}
                }
            }
        }
    }
}, user_class=CustomUser)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_menu(message.chat.id, ['main'])


bot.polling()

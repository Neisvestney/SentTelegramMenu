import os

from tmenu import TelegramMenu

bot = TelegramMenu(os.environ.get("TELEGRAM_TOKEN"), lambda: {
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
            }
        }
    }
})


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_menu(message.chat.id, ['main'])


bot.polling()

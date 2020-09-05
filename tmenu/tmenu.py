import types

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


class TempUser:
    def __init__(self, chat_id, step, menu_id):
        self.menu_id = menu_id
        self.step = step
        self.chat_id = chat_id


class TelegramMenu(telebot.TeleBot):
    def __init__(self, token: str, schema: types.LambdaType, *args, **kwargs):
        super(TelegramMenu, self).__init__(token, *args, **kwargs)

        self.schema = schema
        self.users = list()

        @self.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if self.get_user(call.message.chat.id).step:
                if call.data == 'back':  # If button 'back
                    del self.get_user(call.message.chat.id).step[-1]
                    self.edit_menu(call.message)
                elif 'notification' in self.get_menu(call.message.chat.id)[0]['buttons'][call.data]:  # if notif-button
                    # self.answer_callback_query(call.id, "OK")
                    self.send_notification(
                        self.get_menu(call.message.chat.id)[0]['buttons'][call.data]['notification'], call.message.chat.id
                    )
                elif 'func' in self.get_menu(call.message.chat.id)[0]['buttons'][call.data]:  # if func-button
                    self.get_menu(call.message.chat.id)[0]['buttons'][call.data]['func'](call.message)
                    self.answer_callback_query(call.id, "OK")
                else:  # If submenu
                    self.get_user(call.message.chat.id).step.append(call.data)
                    self.edit_menu(call.message)

    def get_user(self, chat_id) -> TempUser:
        if len(list(filter(lambda x: x.chat_id == chat_id, self.users))) == 0:
            self.users.append(TempUser(chat_id, None, None))
        return list(filter(lambda x: x.chat_id == chat_id, self.users))[0]

    def get_menu(self, chat_id):
        # Возращает текст и клавиатуру меню
        steps = self.get_user(chat_id).step

        menu = self.schema()

        menu = menu[steps[0]]
        for step in steps[1:]:
            menu = menu['buttons'][step]

        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        if 'buttons' in menu:
            [markup.add(InlineKeyboardButton(menu['buttons'][button]['button'], callback_data=button))
             for button in menu['buttons']]

        return menu, markup

    def send_menu(self, chat_id, menu: list = None):
        """
        Send menu to user

        :param chat_id: Id of chat with user
        :param menu: (Optional) If specified set menu to user step. For example: menu = ['main']
        """
        if menu is not None:
            self.get_user(chat_id).step = menu

        menu, markup = self.get_menu(chat_id)
        self.get_user(chat_id).menu_id = self.send_message(chat_id, menu['text'], reply_markup=markup).message_id

    def edit_menu(self, message):
        menu, markup = self.get_menu(message.chat.id)
        self.edit_message_text(menu['text'], message.chat.id, message.message_id, reply_markup=markup)

    def send_notification(self, text, chat_id):
        """
        Send to chat message and resend menu

        :param text Text for sending
        :param chat_id Id of chat with user
        """
        self.delete_message(chat_id, self.get_user(chat_id).menu_id)
        self.send_message(chat_id, text)
        self.send_menu(chat_id)

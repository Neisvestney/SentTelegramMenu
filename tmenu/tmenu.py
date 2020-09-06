import os
import pickle
import types

import telebot
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


class TelegramUser:
    def __init__(self, chat_id, step, menu_id):
        self.menu_id = menu_id
        self.step = step
        self.chat_id = chat_id


class TelegramMenu(telebot.TeleBot):
    def __init__(self, token: str, schema: types.LambdaType, user_class=TelegramUser, database_class=None, save_file='save.dat', *args, **kwargs):
        super(TelegramMenu, self).__init__(token, *args, **kwargs)

        self.schema = schema
        self.user_class = user_class
        self.save_file = save_file

        self.database = database_class() if database_class is not None else None
        self.users = list()

        self.load()

        @self.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if self.get_user(call.message.chat.id).step:
                menu = self.get_menu(call.message.chat.id)[0]['buttons'][call.data]

                if call.data == 'back':  # If button 'back
                    del self.get_user(call.message.chat.id).step[-1]
                    self.edit_menu(call.message)
                elif 'notification' in menu:  # if notif-button
                    # self.answer_callback_query(call.id, "OK")
                    self.send_notification(menu['notification'], call.message.chat.id)
                elif 'func' in menu:  # if func-button
                    menu['func'](call.message, self.get_user(call.message.chat.id))
                    self.answer_callback_query(call.id, "OK")
                elif 'input' in menu:  # if input-button
                    self.get_user(call.message.chat.id).step.append(call.data)
                    self.send_message(call.message.chat.id, menu['input']['text'])
                    self.delete_menu(call.message.chat.id)
                else:  # If submenu
                    self.get_user(call.message.chat.id).step.append(call.data)
                    self.edit_menu(call.message)

                self.save()

        @self.message_handler(func=lambda m: 'input' in self.get_menu(m.chat.id)[0])
        def get_text(message):
            menu = self.get_menu(message.chat.id)[0]['input']
            user = self.get_user(message.chat.id)

            del user.step[-1]

            if 'field' in menu:
                self._set_with_validation(user, menu, 'field', message)
            elif 'db_field' in menu:
                self._set_with_validation(self.database, menu, 'db_field', message)
            elif 'func' in menu:
                menu['func'](message.text)
                self.send_menu(message.chat.id)

            self.save()

    def get_user(self, chat_id) -> TelegramUser:
        if len(list(filter(lambda x: x.chat_id == chat_id, self.users))) == 0:
            self.users.append(self.user_class(chat_id, None, None))
        return list(filter(lambda x: x.chat_id == chat_id, self.users))[0]

    def get_menu(self, chat_id):
        steps = self.get_user(chat_id).step
        if steps is None or len(steps) == 0 or type(steps) is str:
            return [[], None]

        menu = self.schema(chat_id, self.get_user(chat_id))

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
            self.save()

        if self.get_user(chat_id).menu_id is not None:
            try:
                self.delete_message(chat_id, self.get_user(chat_id).menu_id)
            except ApiTelegramException:
                pass

        menu, markup = self.get_menu(chat_id)
        self.get_user(chat_id).menu_id = self.send_message(chat_id, menu['text'], reply_markup=markup).message_id

    def edit_menu(self, message):
        menu, markup = self.get_menu(message.chat.id)
        self.edit_message_text(menu['text'], message.chat.id, message.message_id, reply_markup=markup)

    def delete_menu(self, chat_id):
        self.delete_message(chat_id, self.get_user(chat_id).menu_id)
        self.get_user(chat_id).menu_id = None

    def send_notification(self, text, chat_id):
        """
        Send to chat message and resend menu

        :param text Text for sending
        :param chat_id Id of chat with user
        """
        self.delete_menu(chat_id) if self.get_user(chat_id).menu_id is not None else None
        self.send_message(chat_id, text)
        self.send_menu(chat_id)

    def save(self):
        """
        Save users to file 'save_file'
        """
        if self.save_file is not None:
            with open(self.save_file, 'wb') as f:
                pickle.dump({'users': self.users, 'database': self.database}, f)

    def load(self):
        """
        Load users from file 'save_file'
        :return TelegramMenu
        """
        if self.save_file is not None and os.path.exists(self.save_file):
            with open(self.save_file, 'rb') as f:
                save = pickle.load(f)
                self.users = save['users']
                self.database = save['database']

        return self

    def _set_with_validation(self, obj, menu, field, message):
        if hasattr(obj, f"{menu[field]}_validation"):
            text, value = getattr(obj, f"{menu[field]}_validation")(message.text)
            if text is not None:
                self.send_notification(text, message.chat.id)
            else:
                setattr(obj, menu[field], value)
                self.send_menu(message.chat.id)
        else:
            setattr(obj, menu[field], message.text)
            self.send_menu(message.chat.id)

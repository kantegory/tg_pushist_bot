from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import telebot
import datetime
from telebot import types
# import requests

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = 'YOUR-SPREADSHEET-ID'
SAMPLE_RANGE_NAME = 'YOUR-SAMPLE-RANGE-NAME'


def sheets_connect():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Лист1!A1:D1",
             "majorDimension": "ROWS",
             # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
             "values": [["Время запроса бота", "Время ответа", "Имя пользователя", "Ответ"]]}
        ]
    }).execute()

    return service


def set_sheets_value(service, request_time=None, response_time=None, response_username=None, response_text=None):
    sheet = service.spreadsheets()
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Лист1!A2:D2",
             "majorDimension": "ROWS",
             # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
             "values": [[str(request_time), str(response_time), str(response_username), str(response_text)]]}
        ]
    }).execute()


token = 'YOUR-BOT-TOKEN'
bot = telebot.TeleBot(token)
# telebot.apihelper.proxy = {'https': 'socks5://userproxy:f76847.FCKRKNbot.aiypw.club:500'}


def new_bot(user_token):
    pers_bot = telebot.TeleBot(user_token)
    chat_list = []
    bot_updates = 'https://api.telegram.org/bot' + user_token + '/getUpdates'
    # pers_bot.set_webhook(bot_updates)
    updates = pers_bot.get_updates()
    # print(pers_bot.get_updates())
    # print('https://api.telegram.org/bot' + user_token + '/getUpdates')
    # chats = requests.options('https://api.telegram.org/bot' + user_token + '/getUpdates')
    # # print(chats)
    # chats = pers_bot.get_updates()
    # # print(chats)

    # @pers_bot.callback_query_handler(func=lambda call: True)
    # def

    def set_request():
        set_time()

        @pers_bot.message_handler(content_types=['text'])
        def handle_request(message):
            msg = 'Когда отправить запрос? Напишите ответ в виде 24.01 02:10 или ' \
                      'можете написать только время, чтобы отправить сегодня'
            pers_bot.send_message(message.chat.id, msg, parse_mode='html')

    def set_time():
        set_period()
        @pers_bot.message_handler(content_types=['text'])
        def handle_time(message):
            choose_msg = 'Выберите период или введите его в формате "1 нед", "2 дн", "20 дн"'
            keyboard = types.InlineKeyboardMarkup()

            period_buttons = [{'text': 'Один раз', 'callback': 'period_once'},
                            {'text': '1 день', 'callback': 'period_one_day'},
                            {'text': '2 дня', 'callback': 'period_two_days'},
                            {'text': '4 дня', 'callback': 'period_four_days'},
                            {'text': '1 неделя', 'callback': 'period_one_week'},
                            {'text': '2 недели', 'callback': 'period_two_weeks'},
                            {'text': '4 недели', 'callback': 'period_four_weeks'}]

            for btn in period_buttons:
                text, callback = btn['text'], btn['callback']
                callback_button = types.InlineKeyboardButton(text=text, callback_data=callback)
                keyboard.add(callback_button)

            pers_bot.send_message(message.chat.id, choose_msg, reply_markup=keyboard, parse_mode='html')

    def set_period():
        @pers_bot.callback_query_handler(func=lambda call: True)
        def set_curr_period(call):
            # Если сообщение из чата с ботом
            # set_chat = 'Введите текст запроса в ' + chat.title
            set_period_msg = 'Всё готово'
            if call.message:
                pers_bot.send_message(call.message.chat.id, set_period_msg, parse_mode='html')

    def curr_chat(chat):
        @pers_bot.callback_query_handler(func=lambda call: True)
        def set_curr_chat(call):
            # Если сообщение из чата с ботом
            set_chat = 'Введите текст запроса в ' + chat.title
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="СПИСОК ЧАТОВ", callback_data="chat_list")
            keyboard.add(callback_button)

            # if call.message:
            #     if call.data == chat.id:
            # pers_bot.send_message(call.message.chat.id, set_chat, parse_mode='html')
            # set_request()

        set_chat = 'Введите текст запроса в ' + chat.title
        set_request()

        return set_chat

    @pers_bot.message_handler(commands=['start'])
    def handle_pers_bot_start(message):
        hello_msg = "Добавь новые запросы! \n" \
                    "\n" \
                    "Не забудь убедиться, что я есть в чатах, в которые ты хочешь добавить запрос.\n" \
                    "\n" \
                    "Если захочешь удалить существующий запрос, используй /delete или кнопку внизу. " \
                    "Если передумал, и хочешь начать заново, напиши /new \n" \
                    "\n" \
                    "Чаты для добавления:"

        # print(message.chat)

        if message.chat.type == 'group':
            chat_list.append(message.chat)
        # print(chat_list)

        hello_msg = "Добавь новые запросы! \n" \
                    "\n" \
                    "Не забудь убедиться, что я есть в чатах, в которые ты хочешь добавить запрос.\n" \
                    "\n" \
                    "Если захочешь удалить существующий запрос, используй /delete или кнопку внизу. " \
                    "Если передумал, и хочешь начать заново, напиши /new \n" \
                    "\n" \
                    "Чаты для добавления:"
        keyboard = types.InlineKeyboardMarkup()

        for chat in chat_list:
            callback_button = types.InlineKeyboardButton(text=chat.title, callback_data='set_chat')
            keyboard.add(callback_button)



        callback_button = types.InlineKeyboardButton(text="УДАЛИТЬ ЗАПРОС", callback_data="del_req")
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text="СПИСОК ЧАТОВ", callback_data="chat_list")
        keyboard.add(callback_button)
        sent_message = pers_bot.send_message(message.chat.id, hello_msg, reply_markup=keyboard, parse_mode='html')
        curr_chat(chat_list[0])  # тестируем на единственном чате, который есть в списке
        # print(sent_message)
        # request_time = datetime.datetime.fromtimestamp(sent_message.date)

    @pers_bot.callback_query_handler(func=lambda call: True)
    def callback_pers_bot_inline(call):
        # Если сообщение из чата с ботом
        msg = 'Удалено'
        chat_list_msg = 'Списочек чатиков'
        set_chat = 'Введите текст запроса в '
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="СПИСОК ЧАТОВ", callback_data="chat_list")
        keyboard.add(callback_button)

        if call.message:
            if call.data == "del_req":
                # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
                pers_bot.send_message(call.message.chat.id, msg, parse_mode='html')
            # request_time = datetime.datetime.fromtimestamp(call.message.date)
            # request_text = msg
            # response_time = datetime.datetime.fromtimestamp(call.message.date)
            elif call.data == "chat_list":
                pers_bot.send_message(call.message.chat.id, chat_list_msg, parse_mode='html')
            elif call.data == "set_chat":
                set_chat = curr_chat(chat_list[0])
                pers_bot.send_message(call.message.chat.id, set_chat, parse_mode='html')

    @pers_bot.message_handler(commands=['new'])
    def handle_new_command(message):
        set_chat = curr_chat(chat_list[0])аа
        pers_bot.send_message(message.chat.id, set_chat, parse_mode='html')
        curr_chat(chat_list[0])

    pers_bot.polling(none_stop=True)


@bot.message_handler(commands=['start'])
def handle_start(message):
    hello_msg = "Я помогаю контролировать сотрудников через чаты. \n" \
                "\n" \
                "Напоминаю нужным людям в нужные дни о том, что им нужно делать. " \
                "Попробуй меня и напиши @alantsoff обо мне отзыв."
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="ПОЕХАЛИ", callback_data="newbot")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, hello_msg, reply_markup=keyboard, parse_mode='html')

# Инлайн-режим с непустым запросом
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    kb = types.InlineKeyboardMarkup()
    # Добавляем колбэк-кнопку с содержимым "test"
    kb.add(types.InlineKeyboardButton(text="ПОЕХАЛИ", callback_data="newbot"))
    results = []
    single_msg = types.InlineQueryResultArticle(
        id="1", title="Press me",
        input_message_content=types.InputTextMessageContent(message_text="Я – сообщение из инлайн-режима"),
        reply_markup=kb
    )
    results.append(single_msg)
    bot.answer_inline_query(query.id, results)


# В большинстве случаев целесообразно разбить этот хэндлер на несколько маленьких
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    msg = '1. Перейдите в бот @BotFather и создайте новый бот. \n' \
          '2. После создания бота вы получите токен бота (выглядит вот так – ' \
          '<code>123456:ABC-DEF1234gh...</code>) – ' \
          'скопируйте его сюда и отправьте.'

    if call.message:
        if call.data == "newbot":
            bot.send_message(call.message.chat.id, msg, parse_mode='html')
    # Если сообщение из инлайн-режима


@bot.message_handler(content_types=['text'])
def handle_text(message):
    # message_text = int(''.join(message.text.split()))
    message_text = ''.join(message.text).split()[0]
    if len(message_text) == 45:
        new_bot_token = message_text
        bot.send_message(message.chat.id, 'Спасибо за токен', parse_mode='html')
        new_bot(new_bot_token)
    # request_time = ''
    # response_date = datetime.datetime.fromtimestamp(message.date)
    # response_username = message.from_user.username
    # response_text = message.text
    # print('Время ответа', response_date)  # get date of message
    # print('Username', response_username)   # get username
    # print('Текст', response_text)  # get text of message
    #
    # service = sheets_connect()
    #
    # if message_text < 1000:
    #     sent_message = bot.send_message(message.chat.id, 'Маловато, надо поднажать', parse_mode='html')
    #     # request_time = datetime.datetime.fromtimestamp(sent_message.date)
    #     # print('Время ответа бота', request_time)
    #     print(sent_message)
    # elif message_text < 10000:
    #     sent_message = bot.send_message(message.chat.id, 'Хороший результат, так держать', parse_mode='html')
    #     # request_time = datetime.datetime.fromtimestamp(sent_message.date)
    #     # print('Время ответа бота', request_time)
    #     print(sent_message.text)
    # set_sheets_value(service, None, response_date, response_username, response_text)


if __name__ == '__main__':
    bot.polling(none_stop=True)

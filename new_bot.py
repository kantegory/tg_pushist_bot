import telebot
import datetime
from telegramcalendar import create_calendar, create_month
from telebot import types
from copy import deepcopy
from time import sleep
import threading as th
from db_scripts import *
from googlesheets import *
import json
import sqlite3
from googletrans import Translator


def new_bot(user_token, lang, service, spreadsheet_id):
    'Дата и время запроса Запрос Дата и время ответа	Ответ @username отвечающего Чат'
    telebot.apihelper.proxy = {'https': 'socks5://v3_124570271:5ClzQKYq@s5.priv.opennetwork.cc:1080'}

    bot = telebot.TeleBot(user_token)

    # bot = telebot.TeleBot('761131294:AAH406zzUNqzrGTpMn8eDllELsxM9H6jolI')

    s = session()

    # constants
    tmp_requests = []
    tmp_period = []
    threads = []


    def init_bot_info():
        bot_info = {
            'bot_tg_id': str(bot.get_me().id),
            'bot_username': '@' + str(bot.get_me().username)
        }

        return bot_info

    def translate_to(language_code, msg):

        translator = Translator()
        translated_msg = translator.translate(msg, language_code, 'ru')

        return translated_msg.text

    def init_bot_table():
        bot_info = init_bot_info()
        bot_tg_id = bot_info['bot_tg_id']
        bot_stat = select_bot(bot_tg_id)[0]['bot_stat']
        return bot_stat

    values = [
        ['Текст рассылки', 'Ответ', 'Реакция'],
        ['Сколько денег заработал?', '1000', 'Надо поднажать'],
        ['Сколько денег заработал?', '5000', 'Неплохо'],
        ['Сколько денег заработал?', '10000', 'Отлично продолжай в том же духе']
    ]
    print(values)

    ranges = '{}!A{}:C{}'.format('Рассылки', 1, 5)
    set_sheets_value(service, spreadsheet_id, ranges, values)

    values = [['Дата и время ответа', 'Текст ответа', 'Username', 'Чат', 'Дата и время запроса', 'Запрос']]
    ranges = '{}!A{}:F{}'.format('Ответы на запросы бота', 1, 1)
    set_sheets_value(service, spreadsheet_id, ranges, values)

    ranges = '{}!A{}:C{}'.format('Рассылки', 2, 4)
    # answers = get_sheets_value(service, spreadsheet_id, ranges)
    # print('this is answers attention', answers)

    def set_user_info(user_tg_id, user_name, user_language, user_refer_name):
        user_info = [{
            'user_tg_id': str(user_tg_id),
            'user_name': str(user_name),
            'user_language': str(user_language),
            'user_refer_name': str(user_refer_name)
        }]

        user_add(user_info)

    def set_bot_info(user_id):
        bot_info = [{
            'bot_tg_id': str(bot.get_me().id),
            'bot_username': '@' + str(bot.get_me().username),
            'user_id': user_id
        }]

        bot_add(bot_info)

    def set_request_info(request):

        request_add(request)

    def set_chat_info(chat_tg_id, chat_title, bot_id):
        chat_info = [{
            'chat_tg_id': chat_tg_id,
            'chat_title': chat_title,
            'bot_id': bot_id
        }]

        chat_add(chat_info)

    def set_payment_info(payment_amount, user_id):

        payment_add([{
            'payment_amount': payment_amount,
            'user_id': user_id
        }])

    def get_user_info(user_tg_id):

        return select_user(user_tg_id)

    def get_chat_list(markup, callback_info):
        bot_info = init_bot_info()
        print(select_bot(bot_info['bot_tg_id']))
        bot_id = select_bot(bot_info['bot_tg_id'])[0]['bot_id']
        chat_list = select_chat(bot_id)

        if len(chat_list) > 0:

            for chat in chat_list:
                chat_number = str(chat_list.index(chat)) + ') '
                text = chat_number + chat['chat_title']
                callback_data = callback_info + ';' + chat['chat_tg_id'] + ';' + chat['chat_title']
                callback_button = types.InlineKeyboardButton(text=text, callback_data=callback_data)
                markup.add(callback_button)

    def get_requests_by_chat_id(user_id, chat_id):

        return select_request(user_id, chat_id)

    def get_request_list(markup=None, user_tg_id=None, chat_tg_id=None):
        print(user_tg_id)
        user_id = str(select_user(user_tg_id)[0]['user_id'])
        bot_info = init_bot_info()
        bot_id = select_bot(bot_info['bot_tg_id'])[0]['bot_id']
        chat_id = str(select_chat(bot_id)[0]['chat_id']) if select_chat(bot_id)[0]['chat_tg_id'] == chat_tg_id else None
        print(chat_id)
        requests = get_requests_by_chat_id(user_tg_id, chat_tg_id)  # проверить чтобы было не по тг айди
        print(requests)

        if markup is not None:

            for request in requests:
                request_number = str(requests.index(request)) + ') '
                text = request_number + request['request_text']
                callback_data = 'REQUEST;' + str(user_tg_id) + ';' + str(chat_tg_id) + ';' + str(request['request_id'])
                callback_button = types.InlineKeyboardButton(text=text, callback_data=callback_data)
                markup.add(callback_button)

        return requests

    def get_request_info(requests, request_id):

        request_info = {}

        for request in requests:

            if str(request['request_id']) == request_id:
                print('curr req', request)
                request_info['request_text'] = request['request_text']
                request_info['request_start_date'] = request['request_start_date']
                request_info['request_end_date'] = request['request_end_date']
                request_info['request_time'] = request['request_time']
                request_info['request_period'] = request['request_period']
                request_info['request_period_opts'] = request['request_period_opts']
                request_info['request_chat_id'] = request['request_chat_id']

        return request_info

    def get_period_list(markup=None):

        period_buttons = [
            {'text': translate_to(lang, '1 день'), 'callback_data': 'PERIOD;1'},
            {'text': translate_to(lang, '2 дня'), 'callback_data': 'PERIOD;2'},
            {'text': translate_to(lang, '3 дня'), 'callback_data': 'PERIOD;3'},
            {'text': translate_to(lang, '4 дня'), 'callback_data': 'PERIOD;4'},
            {'text': translate_to(lang, '5 дней'), 'callback_data': 'PERIOD;5'},
            {'text': translate_to(lang, '6 дней'), 'callback_data': 'PERIOD;6'},
            {'text': translate_to(lang, '7 дней'), 'callback_data': 'PERIOD;7'},
            {'text': translate_to(lang, 'Выходные дни'), 'callback_data': 'PERIOD;R'},
            {'text': translate_to(lang, 'Будние дни'), 'callback_data': 'PERIOD;W'},
            {'text': translate_to(lang, 'Каждый конкретный день недели'), 'callback_data': 'PERIOD;D'},
            {'text': translate_to(lang, 'Каждое конкретное число месяца'), 'callback_data': 'PERIOD;N'}
        ]

        if markup is not None:

            for btn in period_buttons:
                text, callback_data = btn['text'], btn['callback_data']

                callback_button = types.InlineKeyboardButton(text=text, callback_data=callback_data)
                markup.add(callback_button)
        else:

            return period_buttons

    def get_period_weekdays(markup=None):

        weekdays_buttons = [{'text': 'Mo', 'callback_data': 'WEEK;1;0'},
                            {'text': 'Tu', 'callback_data': 'WEEK;2;0'},
                            {'text': 'We', 'callback_data': 'WEEK;3;0'},
                            {'text': 'Th', 'callback_data': 'WEEK;4;0'},
                            {'text': 'Fr', 'callback_data': 'WEEK;5;0'},
                            {'text': 'Sa', 'callback_data': 'WEEK;6;0'},
                            {'text': 'Su', 'callback_data': 'WEEK;7;0'},
                            {'text': translate_to(lang, 'Подтвердить'), 'callback_data': 'WEEK;A;0'},
                            {'text': translate_to(lang, 'Назад'), 'callback_data': 'WEEK;B;0'}]

        if markup is not None:

            for btn in weekdays_buttons:
                text, callback_data = btn['text'], btn['callback_data']

                callback_button = types.InlineKeyboardButton(text=text, callback_data=callback_data)
                markup.add(callback_button)

        else:

            return weekdays_buttons

    def get_back_to_start(message):
        user_tg_id, user_name, user_language = str(message.from_user.id), str(message.from_user.username), str(
            message.from_user.language_code)
        user_refer_name = 'test'
        set_user_info(user_tg_id, user_name, user_language, user_refer_name)
        handle_msg = 'Добавь новые запросы! \n' \
                     '\n' \
                     'Не забудь убедиться, что я есть ' \
                     'в чатах, в которые ты хочешь добавить запрос.\n' \
                     '\n' \
                     'Чаты для добавления:'
        handle_msg = translate_to(lang, handle_msg)
        markup = types.InlineKeyboardMarkup()

        if message.chat.type == 'private':
            get_chat_list(markup, 'CHAT')

            callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Мои рассылки'), callback_data='SHOW_REQ')
            markup.add(callback_button)

            bot.send_message(message.chat.id, handle_msg, reply_markup=markup)

    def format_period(period):
        # дописать, вроде готово
        period, period_opts = period['period'], period['period_opts']
        weekdays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

        if 'weekdays' in period_opts.lower():

            if len(period) > 1:

                period = period.split(',')

                for i in range(len(weekdays)):
                    for j in range(len(period)):
                        period[j] = weekdays[int(period[j])]

                period = translate_to(lang, 'Каждый {}').format(','.join(period))

            else:

                period = weekdays[int(period)]
                period = 'Каждый {}'.format(period)

        elif 'every' in period_opts.lower():
            curr_period = period

            if curr_period == '1':
                period = 'Каждый день'
            elif curr_period in ['2', '3', '4']:
                period = 'Каждые ' + curr_period + ' дня'
            elif curr_period in ['5', '6', '7']:
                period = 'Каждые ' + curr_period + ' дней'
            elif curr_period == 'R':
                period = 'Каждые выходные'
            elif curr_period == 'W':
                period = 'Будни'

        elif 'monthdays' in period_opts.lower():

            period = 'Каждое {} число месяца'.format(period)

        return translate_to(lang, period)

    # handlers are start here
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        get_back_to_start(message)

    @bot.callback_query_handler(func=lambda call: call.data == "START")
    def handle_start(message):

        get_back_to_start(message)

    # handle event, when bot was added in chat
    @bot.message_handler(content_types=['new_chat_members'])
    def handle_new_chat(message):

        bot_info = init_bot_info()

        if str(message.new_chat_member.id) == bot_info['bot_tg_id']:
            chat_tg_id = message.chat.id
            chat_title = message.chat.title

            bot_id = select_bot(bot_info['bot_tg_id'])[0]['bot_id']

            set_chat_info(chat_tg_id, chat_title, bot_id)

    @bot.callback_query_handler(func=lambda call: 'CHAT' in call.data)
    def handle_chat_query(call):

        info = call.data.split(sep=';')
        chat_tg_id, chat_title = info[1], info[2]

        handle_chat_query_msg = translate_to(lang, 'Введите текст рассылки в {}').format(chat_title)

        markup = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Назад'), callback_data='back')
        markup.add(callback_button)

        sent_msg = bot.edit_message_text(handle_chat_query_msg, call.message.chat.id, call.message.message_id,
                                         reply_markup=markup)
        bot.register_next_step_handler(sent_msg, handle_request_text)

    def handle_request_text(message):

        # write in temp arr
        tmp_requests.append({})
        requests_count = len(tmp_requests) - 1
        tmp_requests[requests_count]['request_text'] = message.text

        handle_request_text_msg = translate_to(lang, 'Выберите дату начала: \n')

        # this is markup
        start_date = create_calendar(callback_info='START')
        bot.send_message(message.chat.id, handle_request_text_msg, reply_markup=start_date)

    @bot.callback_query_handler(func=lambda call: 'DAY' in call.data)
    def handle_date_query(call):

        info = call.data.split(';')
        callback_info = info[0].split('-')[0]
        year, month, day = info[1], info[2], info[3]
        start_date = '{}.{}.{}'.format(day, month, year)

        handle_date_query_msg = translate_to(lang, 'Выбранная дата: {}').format(start_date)

        markup = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Подтвердить'),
                                                     callback_data=callback_info + '-ACCEPT;' + start_date)
        markup.add(callback_button)
        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Изменить'),
                                                     callback_data=callback_info + '-EDIT')
        markup.add(callback_button)

        bot.edit_message_text(handle_date_query_msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: 'MONTH' in call.data)
    def handle_month_query(call):

        info = call.data.split(';')
        callback_info = info[0].split('-')[0]
        month_opt = info[0].split('-')[1]
        year, month = int(info[1]), int(info[2])

        if month_opt == 'PREV':
            month -= 1

        elif month_opt == 'NEXT':
            month += 1

        if month < 1:
            month = 12
            year -= 1

        if month > 12:
            month = 1
            year += 1

        opt_msg = 'начала' if callback_info == 'START' else 'окончания'
        handle_month_query_msg = translate_to(lang, 'Выберите дату {}: \n'.format(opt_msg))

        markup = create_calendar(year, month, callback_info)

        bot.edit_message_text(handle_month_query_msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: 'IGNORE' in call.data)
    def handle_ignore_query(call):

        handle_ignore_query_msg = translate_to(lang,'Вы нажали не туда!')

        bot.answer_callback_query(call.id, text=handle_ignore_query_msg)

    @bot.callback_query_handler(func=lambda call: 'ACCEPT' in call.data)
    def handle_date_accept_query(call):

        info = call.data.split(';')
        callback_info = info[0].split('-')[0]
        date = info[1]

        requests_count = len(tmp_requests) - 1
        tmp_requests[requests_count]['request_' + callback_info.lower() + '_date'] = date

        handle_date_accept_query_msg = translate_to(lang,'Дата выбрана!')

        bot.answer_callback_query(call.id, text=handle_date_accept_query_msg)

        if callback_info == 'START':

            set_period(call)

        elif callback_info == 'END':

            handle_date_accept_query_msg = translate_to(lang,'Рассылка создана!')

            bot.edit_message_text(handle_date_accept_query_msg, call.message.chat.id, call.message.message_id)

            # save request to db
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            set_request_info(tmp_requests)
            set_request(tmp_requests[requests_count], user_id, chat_id)

            get_back_to_start(call.message)

    @bot.callback_query_handler(func=lambda call: 'EDIT' in call.data)
    def handle_edit_date_query(call):

        info = call.data.split(';')
        callback_info = info[0].split('-')[0]

        opt_msg = 'начала' if callback_info == 'START' else 'окончания'
        handle_edit_date_query_msg = translate_to(lang,'Выберите дату {}: \n'.format(opt_msg))

        # this is markup
        markup = create_calendar(callback_info=callback_info)
        bot.edit_message_text(handle_edit_date_query_msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    def set_period(call):

        set_period_msg = translate_to(lang,'Выберите период отправки сообщениий: \n')

        markup = types.InlineKeyboardMarkup()

        get_period_list(markup)

        bot.edit_message_text(set_period_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: 'PERIOD' in call.data)
    def handle_period_query(call):

        info = call.data.split(sep=';')
        period = info[1]

        chat_tg_id = call.from_user.id
        message_tg_id = call.message.message_id

        set_period_opts(period, chat_tg_id, message_tg_id)

    def set_period_opts(period, chat_tg_id, message_tg_id):

        if period in [str(x) for x in range(1, 8)] or period in 'RW':

            set_period_opts_msg = translate_to(lang, "Введите время отправки (в формате 22:10):")

            sent_message = bot.edit_message_text(set_period_opts_msg, chat_tg_id, message_tg_id)
            bot.register_next_step_handler(sent_message, set_end_date)

            requests_count = len(tmp_requests) - 1
            tmp_requests[requests_count]['request_period'] = period
            tmp_requests[requests_count]['request_period_opts'] = 'EVERY;' + period + ';DAY'

        elif period == 'D':

            set_period_opts_msg = translate_to(lang, "Выберите дни недели:")

            markup = types.InlineKeyboardMarkup()

            get_period_weekdays(markup)

            bot.edit_message_text(set_period_opts_msg, chat_tg_id, message_tg_id, reply_markup=markup)

        elif period == 'N':

            set_month_dates_msg = translate_to(lang, "Выберите числа месяца для отправки:")

            markup = json.dumps(create_month())

            bot.edit_message_text(set_month_dates_msg, chat_tg_id, message_tg_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: 'WEEK' in call.data)
    def handle_period_weekday_query(call):

        info = call.data.split(sep=';')
        print(info)
        period = info[1]
        # state = info[2]

        chat_tg_id = call.message.chat.id
        message_tg_id = call.message.message_id

        if period in [str(x) for x in range(1, 8)]:

            tick_button(call)

            set_period_opts_msg = translate_to(lang, "Выберите дни недели:")

            markup = types.InlineKeyboardMarkup()

            for weekday in weekdays:
                text, callback_data = weekday['text'], weekday['callback_data']
                callback_button = types.InlineKeyboardButton(text=text, callback_data=callback_data)
                markup.add(callback_button)

            bot.edit_message_text(set_period_opts_msg, call.message.chat.id, call.message.message_id,
                                  reply_markup=markup)

        elif period == 'A':

            set_period_opts_msg = translate_to(lang, "Введите время отправки (в формате 22:10):")

            requests_count = len(tmp_requests) - 1

            tmp_requests[requests_count]['request_period'] = ','.join(period)
            tmp_requests[requests_count]['request_period_opts'] = 'WEEKDAYS;' + ','.join(period)

            sent_message = bot.edit_message_text(set_period_opts_msg, chat_tg_id, message_tg_id)
            bot.register_next_step_handler(sent_message, set_end_date)

        elif period == 'B':

            set_period(call)

    @bot.callback_query_handler(func=lambda call: 'DATE' in call.data)
    def handle_period_weekday_query(call):

        info = call.data.split(sep=';')
        period = info[1]

        chat_tg_id = call.message.chat.id
        message_tg_id = call.message.message_id

        if period in [str(x) for x in range(1, 32)]:

            tick_button(call)

            set_period_opts_msg = translate_to(lang, "Выберите числа месяца:")

            markup = json.dumps(monthdays)

            bot.edit_message_text(set_period_opts_msg, call.message.chat.id, call.message.message_id,
                                  reply_markup=markup)

        elif period == 'A':

            set_period_opts_msg = translate_to(lang, "Введите время отправки (в формате 22:10):")

            requests_count = len(tmp_requests) - 1

            tmp_requests[requests_count]['request_period'] = ','.join(period)
            tmp_requests[requests_count]['request_period_opts'] = 'MONTHDAYS;' + ','.join(period)

            sent_message = bot.edit_message_text(set_period_opts_msg, chat_tg_id, message_tg_id)
            bot.register_next_step_handler(sent_message, set_end_date)

        elif period == 'B':

            set_period(call)

    weekdays = get_period_weekdays()
    monthdays = create_month()

    def tick_button(call):

        info = call.data.split(sep=';')

        option = info[0]
        period = info[1]
        state = int(info[2])

        if state == 0:

            tmp_period.append(period)

            if option == 'WEEK':

                for i in range(len(weekdays)):
                    if weekdays[i]['callback_data'] == call.data:
                        weekdays[i]['text'] = '✓ ' + weekdays[i]['text']
                        weekdays[i]['callback_data'] = set_new_callback_data(info, '1')

            elif option == 'DATE':

                for i in range(len(monthdays['inline_keyboard'])):
                    for j in range(len(monthdays['inline_keyboard'][i])):
                        if monthdays['inline_keyboard'][i][j]['callback_data'] == call.data:
                            monthdays['inline_keyboard'][i][j]['text'] = '✓ ' + monthdays['inline_keyboard'][i][j][
                                'text']
                            monthdays['inline_keyboard'][i][j]['callback_data'] = set_new_callback_data(info, '1')

        elif state == 1:

            tmp_period.remove(period)

            if option == 'WEEK':

                for i in range(len(weekdays)):
                    if weekdays[i]['callback_data'] == call.data:
                        weekdays[i]['text'] = weekdays[i]['text'][2:]
                        weekdays[i]['callback_data'] = set_new_callback_data(info, '0')

            elif option == 'DATE':

                for i in range(len(monthdays['inline_keyboard'])):
                    for j in range(len(monthdays['inline_keyboard'][i])):
                        if monthdays['inline_keyboard'][i][j]['callback_data'] == call.data:
                            monthdays['inline_keyboard'][i][j]['text'] = monthdays['inline_keyboard'][i][j]['text'][2:]
                            monthdays['inline_keyboard'][i][j]['callback_data'] = set_new_callback_data(info, '0')

    def set_new_callback_data(callback_data, new_state):

        new_callback_data = callback_data[:-1]
        new_callback_data.append(new_state)
        new_callback_data = ';'.join(new_callback_data)

        return new_callback_data

    def set_end_date(message):

        requests_count = len(tmp_requests) - 1
        tmp_requests[requests_count]['request_time'] = message.text
        tmp_requests[requests_count]['user_id'] = message.from_user.id
        tmp_requests[requests_count]['chat_id'] = message.chat.id

        set_end_date_msg = translate_to(lang, 'Выберите дату окончания:')

        markup = create_calendar(callback_info='END')

        bot.send_message(message.chat.id, set_end_date_msg, reply_markup=markup)

    def set_request(request, user_id, chat_id):

        requests = get_request_list(None, user_id, chat_id)
        request_id = 0

        for _request in requests:
            request_id = str(_request['request_id']) if _request['request_text'] == request['request_text'] and str(
                _request['request_chat_id']) == str(request['chat_id']) else 0
        # print('request_id', type(request_id))
        request_info = get_request_info(requests, request_id)
        print(request_info)
        set_request_thread(request_info)

    def set_request_thread(request_info):

        threads.append({})
        threads_count = len(threads) - 1

        threads[threads_count]['target'] = send_request
        threads[threads_count]['name'] = "Request " + str(threads_count) + " thread"
        threads[threads_count]['args'] = request_info
        threads[threads_count]['daemon'] = True

        new_request_thread = th.Thread(target=threads[threads_count]['target'], name=threads[threads_count]['name'],
                                       args=([threads[threads_count]['args']]), daemon=threads[threads_count]['daemon'])

        new_request_thread.start()

        return new_request_thread

    def send_request(request):

        curr_request = deepcopy(request)
        # request = request[0]
        curr_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        curr_time = datetime.datetime.now().strftime('%H:%M')
        today = datetime.datetime.today()
        request_start_date = request['request_start_date'] + ' ' + request['request_time']
        request_end_date = request['request_end_date'] + ' ' + request['request_time']
        request_chat_id = request['request_chat_id']
        request_period = request['request_period']
        request_period_opts = request['request_period_opts']
        request_text = request['request_text']

        if request_start_date <= curr_date <= request_end_date:

            if "WEEKDAYS" in request_period_opts:

                for _period in request_period.split(','):

                    if int(_period) == today.weekday() and curr_time == request['request_time']:

                        sent_request = bot.send_message(request_chat_id, request_text)
                        add_request_to_sheet(sent_request)
                        bot.register_next_step_handler(sent_request, get_bot_answer)

                    else:

                        sleep(1)
                        send_request(curr_request)

            elif 'EVERY' in request_period_opts:
                # дописать
                # interval = get_interval(request['request_start_date'], request['request_end_date'])
                if curr_time == request['request_time']:

                    sent_request = bot.send_message(request_chat_id, request_text)
                    bot.register_next_step_handler(sent_request, get_bot_answer)

                    sleep(86400 * request_period)
                    send_request(curr_request)

                else:

                    sleep(1)
                    send_request(curr_request)

            elif 'MONTHDAYS' in request_period_opts:

                for _period in request_period:

                    if today.day == int(_period) and curr_time == request['request_time']:

                        sent_request = bot.send_message(request_chat_id, request_text)
                        bot.register_next_step_handler(sent_request, get_bot_answer)

                    else:

                        sleep(1)
                        send_request(curr_request)

    def add_request_to_sheet(message):
        request_sent_date = datetime.datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M')
        request_sent_text = message.text
        ranges = '{}!E{}:F{}'.format('Ответы на запросы бота', 2, 2)
        values = [[request_sent_date, request_sent_text]]
        # pass
        # 'Дата и время ответа	Ответ	Дата и время запроса	Запрос	@username отвечающего	Чат '
        # message.
        '''
        attention {'content_type': 'text', 'message_id': 145, 'from_user': {'id': 124570271, 'is_bot': False, 'first_name': 'David', 'username': 'kantegory', 'last_name': 'Dobryakov', 'language_code': 'ru'}, 'date': 1566585367, 'chat': {'type': 'private', 'last_name': 'Dobryakov', 'first_name': 'David', 'username': 'kantegory', 'id': 124570271, 'title': None, 'all_members_are_administrators': None, 'photo': None, 'description': None, 'invite_link': None, 'pinned_message': None, 'sticker_set_name': None, 'can_set_sticker_set': None}, 'forward_from_chat': None, 'forward_from': None, 'forward_date': None, 'reply_to_message': None, 'edit_date': None, 'media_group_id': None, 'author_signature': None, 'text': '/start', 'entities': [<telebot.types.MessageEntity object at 0x7fe6a35c6ac8>], 'caption_entities': None, 'audio': None, 'document': None, 'photo': None, 'sticker': None, 'video': None, 'video_note': None, 'voice': None, 'caption': None, 'contact': None, 'location': None, 'venue': None, 'new_chat_member': None, 'new_chat_members': None, 'left_chat_member': None, 'new_chat_title': None, 'new_chat_photo': None, 'delete_chat_photo': None, 'group_chat_created': None, 'supergroup_chat_created': None, 'channel_chat_created': None, 'migrate_to_chat_id': None, 'migrate_from_chat_id': None, 'pinned_message': None, 'invoice': None, 'successful_payment': None, 'connected_website': None, 'json': {'message_id': 145, 'from': {'id': 124570271, 'is_bot': False, 'first_name': 'David', 'last_name': 'Dobryakov', 'username': 'kantegory', 'language_code': 'ru'}, 'chat': {'id': 124570271, 'first_name': 'David', 'last_name': 'Dobryakov', 'username': 'kantegory', 'type': 'private'}, 'date': 1566585367, 'text': '/start', 'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]}}
        '''
        set_sheets_value(service, spreadsheet_id, ranges, values)


    def get_interval(start, end):

        start = start.split(sep='.')
        start = [int(c) for c in start]
        start = datetime.datetime(start[2], start[1], start[0])

        end = end.split(sep='.')
        end = [int(c) for c in end]
        end = datetime.datetime(end[2], end[1], end[0])

        interval = end - start

        return interval.days

    def get_bot_answer(message):
        bot.clear_step_handler_by_chat_id(message.chat.id)
        print(message)
        ranges = '{}!A{}:C{}'.format('Рассылки', 2, 4)
        answers = get_sheets_value(service, spreadsheet_id, ranges)
        print(answers)
        # 'Дата и время ответа	Ответ	Дата и время запроса	Запрос	@username отвечающего	Чат '

        bot.send_message(message.chat.id, 'ответ')
        answer_sent_date = datetime.datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M')
        answer_sent_text = message.text
        answer_sent_username = message.from_user.username
        answer_sent_chat = message.chat.title

        ranges = '{}!A{}:D{}'.format('Ответы на запросы бота', 2, 2)
        values = [[answer_sent_date, answer_sent_text, answer_sent_username, answer_sent_chat]]
        set_sheets_value(service, spreadsheet_id, ranges, values)

    @bot.callback_query_handler(func=lambda call: call.data == "SHOW_REQ")
    def handle_show_req_query(call):

        handle_show_req_query_msg = translate_to(lang, 'Выберите чат, в котором хотите просмотреть рассылку: \n')

        markup = types.InlineKeyboardMarkup()

        get_chat_list(markup, 'SHOW_REQ_LIST')

        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Назад'), callback_data='START')
        markup.add(callback_button)

        bot.edit_message_text(handle_show_req_query_msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: 'SHOW_REQ_LIST' in call.data)
    def handle_show_req_list_query(call):

        info = call.data.split(';')
        user_tg_id = call.from_user.id
        chat_tg_id, chat_title = info[1], info[2]

        markup = types.InlineKeyboardMarkup()

        request_list = get_request_list(markup, user_tg_id, chat_tg_id)

        if len(request_list) > 0:
            handle_show_req_list_query_msg = translate_to(lang, 'Рассылки в чате {}: \n').format(chat_title)
        else:
            handle_show_req_list_query_msg = translate_to(lang, 'Рассылок в чате {} нет \n').format(chat_title)

        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Добавить'),
                                                     callback_data='CHAT;{};{}'.format(chat_tg_id, chat_title))
        markup.add(callback_button)
        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Назад'), callback_data='SHOW_REQ')
        markup.add(callback_button)

        bot.edit_message_text(handle_show_req_list_query_msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: 'REQUEST' in call.data)
    def handle_curr_request_query(call):

        info = call.data.split(sep=';')
        user_id, chat_id, request_id = info[1], info[2], info[3]
        print(call.data)
        requests = get_requests_by_chat_id(user_id, chat_id)
        print(requests)
        request_info = get_request_info(requests, request_id)
        print(request_info)
        bot_info = init_bot_info()
        bot_id = select_bot(bot_info['bot_tg_id'])[0]['bot_id']
        chat_tg_id, chat_title = select_chat(bot_id)[0]['chat_tg_id'], select_chat(bot_id)[0]['chat_title']

        # get pretty period
        period = {'period': request_info['request_period'], 'period_opts': request_info['request_period_opts']}
        period = format_period(period)

        show_curr_request_msg = 'Текст: {} \n' \
                                'Дата начала: {} \n' \
                                'Дата окончания: {} \n' \
                                'Периодичность: {} \n' \
                                'Время рассылки: {}'

        show_curr_request_msg = translate_to(lang, show_curr_request_msg).format(request_info['request_text'],
                                                                                 request_info['request_start_date'],
                                                                                 request_info['request_end_date'],
                                                                                 period, request_info['request_time'])

        markup = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Удалить'),
                                                     callback_data='DEL_REQ;{};{};{}'.format(request_id,
                                                                                             chat_tg_id,
                                                                                             chat_title))
        markup.add(callback_button)
        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Назад'),
                                                     callback_data='SHOW_REQ_LIST;{};{}'.format(chat_tg_id,
                                                                                                chat_title))
        markup.add(callback_button)

        bot.edit_message_text(show_curr_request_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: 'DEL_REQ' in call.data)
    def handle_del_req_query(call):

        info = call.data.split(sep=';')

        request_id, chat_tg_id, chat_title = info[1], info[2], info[3]

        delete_request(request_id)

        handle_del_req_query_msg = translate_to(lang, 'Рассылка успешно удалена.')
        bot.answer_callback_query(call.id, text=handle_del_req_query_msg)

        user_tg_id = call.from_user.id

        markup = types.InlineKeyboardMarkup()

        request_list = get_request_list(markup, user_tg_id, chat_tg_id)

        if len(request_list) > 0:
            handle_show_req_list_query_msg = translate_to(lang, 'Рассылки в чате {}: \n').format(chat_title)
        else:
            handle_show_req_list_query_msg = translate_to(lang, 'Рассылок в чате {} нет \n').format(chat_title)

        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Добавить'),
                                                     callback_data='CHAT;{};{}'.format(chat_tg_id, chat_title))
        markup.add(callback_button)
        callback_button = types.InlineKeyboardButton(text=translate_to(lang, 'Назад'),
                                                     callback_data='SHOW_REQ')
        markup.add(callback_button)

        bot.edit_message_text(handle_show_req_list_query_msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    bot.polling()


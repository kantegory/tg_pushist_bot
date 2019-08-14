import telebot
from telebot import types
from copy import deepcopy
from time import sleep
import datetime


def new_bot(user_token):
    telebot.apihelper.proxy = {'https': 'socks5://userproxy:password@ip:port'}
#     user_token = 'YOUR-BOT-TOKEN'
    # pers_bot = telebot.TeleBot(user_token)
    bot = telebot.TeleBot(user_token)

    chat_list = []
    chat_count = 0
    requests = []
    requests_count = 0
    current_shown_dates = {}

    # все вспомогательные функции пойдут в utils
    def set_language(language_code):
        pass

    def get_chat_list(message):
        if message.chat.type == "group":
            chat_list.append(message.chat)
        return chat_list

    def get_chat_list_btns(keyboard):
        btns = []
        for chat in chat_list:
            if chat.title not in btns:
                btns.append(chat.title)
                update_chat_count()
            callback_button = types.InlineKeyboardButton(text=chat.title, callback_data=chat.id)
            keyboard.add(callback_button)

    def update_requests_count(event):
        if event == 'add':
            return requests_count + 1
        elif event == 'del':
            return requests_count - 1

    def update_chat_count():
        return chat_count + 1

    def set_chat(chat, call):
        requests.append({})
        requests[requests_count]['chat'] = chat.id
        set_chat = 'Введите текст запроса в ' + chat.title
        bot.send_message(call.message.chat.id, set_chat, parse_mode='html')

        update_requests_count('add')

        set_request()

    def set_request():
        # set_time()

        @bot.message_handler(content_types=['text'])
        def handle_request(message):
            requests.append({})
            requests[requests_count]['text'] = message.text

            msg = 'Когда отправить запрос? Напишите ответ в виде 24.01 02:10 или ' \
                  'можете написать только время, чтобы отправить сегодня'
            sent_msg = bot.send_message(message.chat.id, msg, parse_mode='html')

            bot.register_next_step_handler(sent_msg, set_time)

    def set_time(message):
        # set_period()
        requests[requests_count]['time'] = message.text

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

        bot.send_message(message.chat.id, choose_msg, reply_markup=keyboard, parse_mode='html')

    def set_period():
        @bot.callback_query_handler(func=lambda call: True)
        def set_curr_period(call):
            requests[requests_count]['period'] = call.message.text

            set_period_msg = 'Всё готово'
            bot.send_message(call.message.chat.id, set_period_msg, parse_mode='html')

            send_request(requests[requests_count])

    @bot.message_handler(commands=['time'])
    def get_calendar(message):
        # now = datetime.datetime.now()  # Current date
        # chat_id = message.chat.id
        # date = (now.year,now.month)
        # current_shown_dates[chat_id] = date  # Saving the current date in a dict

        markup = create_time()
        bot.send_message(message.chat.id, "Выберите время:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: "TIME" in call.data)
    def set_time(call):
        time = call.data[5:7] if ';' not in call.data[5:7] else call.data[5:6]
        print(time)
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text='ПОДТВЕРДИТЬ', callback_data='accept_time')
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='ИЗМЕНИТЬ', callback_data='edit_time')
        keyboard.add(callback_button)
        bot.edit_message_text("Выбранное время:\n" + str(time) + ":00", call.from_user.id, call.message.message_id,
                              reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == 'edit_time')
    def set_time(call):
        markup = create_time()
        bot.edit_message_text("Изменить время:\n", call.from_user.id, call.message.message_id,
                              reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'accept_time')
    def set_time(call):
        bot.edit_message_text("Время выбрано!", call.from_user.id, call.message.message_id)

    @bot.message_handler(commands=['calendar'])
    def get_calendar(message):
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict

        markup = create_calendar(now.year, now.month)
        bot.send_message(message.chat.id, "Выберите дату:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == "edit_data")
    def get_calendar(call):
        message = call.message
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict

        markup = create_calendar(now.year, now.month)
        bot.edit_message_text("Изменить дату:", call.from_user.id, call.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == "accept_data")
    def get_calendar(call):
        message = call.message
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict

        markup = create_calendar(now.year, now.month)
        bot.edit_message_text("Дата выбрана!", call.from_user.id, call.message.message_id)

    @bot.callback_query_handler(func=lambda call: 'DAY' in call.data[0:13])
    def get_day(call):
        chat_id = call.message.chat.id
        saved_date = current_shown_dates.get(chat_id)

        if saved_date is not None:
            day = call.data[12:] if ';' not in call.data[12:] else call.data[11:]
            print(day)
            date = datetime.datetime(int(saved_date[0]), int(saved_date[1]), int(day), 0, 0, 0)
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='ПОДТВЕРДИТЬ', callback_data='accept_data')
            keyboard.add(callback_button)
            callback_button = types.InlineKeyboardButton(text='ИЗМЕНИТЬ', callback_data='edit_data')
            keyboard.add(callback_button)
            bot.edit_message_text("Выбранная дата:\n" + str(date), call.from_user.id, call.message.message_id,
                                  reply_markup=keyboard)
            # bot.send_message(chat_id, str(date), reply_markup=keyboard)
            bot.answer_callback_query(call.id, text="")

        else:
            # add your reaction for shown an error
            pass

    @bot.callback_query_handler(func=lambda call: 'NEXT-MONTH' in call.data)
    def next_month(call):
        chat_id = call.message.chat.id
        saved_date = current_shown_dates.get(chat_id)
        if saved_date is not None:
            year, month = saved_date
            month += 1
            if month > 12:
                month = 1
                year += 1
            date = (year, month)
            current_shown_dates[chat_id] = date
            markup = create_calendar(year, month)
            bot.edit_message_text("Выберите дату:", call.from_user.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        else:
            # add your reaction for shown an error
            pass

    @bot.callback_query_handler(func=lambda call: 'PREV-MONTH' in call.data)
    def previous_month(call):
        chat_id = call.message.chat.id
        saved_date = current_shown_dates.get(chat_id)
        if saved_date is not None:
            year, month = saved_date
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            date = (year, month)
            current_shown_dates[chat_id] = date
            markup = create_calendar(year, month)
            bot.edit_message_text("Выберите дату:", call.from_user.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        else:
            # add your reaction for shown an error
            pass

    @bot.callback_query_handler(func=lambda call: "IGNORE" in call.data)
    def ignore(call):
        bot.answer_callback_query(call.id, text="smth wrong")

    def send_request(request):
        curr_request = deepcopy(request)
        print('current request:', curr_request)
        chat, text, time, period = request['chat'], request['text'], request['time'], request['period']
        curr_datetime = datetime.datetime.now().strftime("%m.%d %H:%M")
        curr_time = datetime.datetime.now().strftime("%H:%M")
        if curr_datetime == time or curr_time == time:
            response_message = bot.send_message(chat, text, parse_mode='html')
            bot.register_next_step_handler(response_message, get_response)
        elif curr_datetime < time or curr_time < time:
            sleep(60)
            send_request(curr_request)

    def get_response(response_message):
        # response_message = response_message.text
        print('im here bro')
        if 999 < response_message < 9999:
            bot.send_message(response_message.chat.id, 'Надо больше')
        elif response_message > 10000:
            bot.send_message(response_message.chat.id, 'Сас, бро))')

    def in_private():
        pass

    def in_group():
        pass

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        language_code = message.from_user.language_code
        set_language(language_code)

        hello_msg = "Добавь новые запросы! \n" \
                    "\n" \
                    "Не забудь убедиться, что я есть и запущен (используй команду /start) " \
                    "в чатах, в которые ты хочешь добавить запрос.\n" \
                    "\n" \
                    "Если захочешь удалить существующий запрос, используй /delete или кнопку внизу. " \
                    "Если передумал, и хочешь начать заново, напиши /new \n" \
                    "\n" \
                    "Чаты для добавления:"
        print(message.from_user.language_code)
        keyboard = types.InlineKeyboardMarkup()
        get_chat_list(message)
        if message.chat.type == "private":
            get_chat_list_btns(keyboard)

        callback_button = types.InlineKeyboardButton(text="Удалить запросы", callback_data="del_req")
        keyboard.add(callback_button)
        bot.send_message(message.chat.id, hello_msg, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if call.message:
            if call.data == "del_req":
                bot.send_message(call.message.chat.id, "Удалено", parse_mode='html')
            elif str(call.data) == str(chat_list[chat_count].id):
                # bot.send_message(call.message.chat.id, "Чат выбран", parse_mode='html')
                set_chat(chat_list[chat_count], call)
            else:
                requests[requests_count]['period'] = call.data

                set_period_msg = 'Всё готово'
                bot.send_message(call.message.chat.id, set_period_msg, parse_mode='html')

                send_request(requests[requests_count])

    bot.polling(none_stop=True)


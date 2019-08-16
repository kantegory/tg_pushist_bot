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

    current_shown_dates = {}
    chat_list = []
    chat_count = 0
    requests = []
    requests_count = 0
    threads = []


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
            callback_button = types.InlineKeyboardButton(text=chat.title, callback_data="CHAT;" + str(chat.id) + ";" + str(chat.title))
            keyboard.add(callback_button)


    def update_chat_count():
        return chat_count + 1


    def update_requests_count(event):
        if event == 'add':
            return requests_count + 1
        elif event == 'del':
            return requests_count - 1


    @bot.message_handler(commands=['start'])
    def handle_start(message):
        language_code = message.from_user.language_code
        # set_language(language_code)

        hello_msg = "Добавь новые запросы! \n" \
                    "\n" \
                    "Не забудь убедиться, что я есть и запущен (используй команду /start) " \
                    "в чатах, в которые ты хочешь добавить запрос.\n" \
                    "\n" \
                    "Если захочешь удалить существующий запрос, используй /delete или кнопку внизу. " \
                    "Если передумал, и хочешь начать заново, напиши /new \n" \
                    "\n" \
                    "Чаты для добавления:"

        keyboard = types.InlineKeyboardMarkup()
        get_chat_list(message)

        if message.chat.type == "private":
            get_chat_list_btns(keyboard)

        callback_button = types.InlineKeyboardButton(text="Мои запросы", callback_data="show_req")
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text="Удалить запросы", callback_data="del_req")
        keyboard.add(callback_button)
        bot.send_message(message.chat.id, hello_msg, reply_markup=keyboard)


    @bot.callback_query_handler(func=lambda call: "CHAT" in call.data)
    def set_chat(call):
        last_sep = call.data.rfind(';')
        set_chat_id = call.data[5:last_sep]
        set_chat_title = call.data[last_sep + 1:]

        requests.append({})
        update_requests_count('add')

        requests[requests_count]['chat_id'] = set_chat_id
        requests[requests_count]['chat_title'] = set_chat_title

        set_chat_msg = "Введите текст рассылки в " + set_chat_title

        sent_set_chat_msg = bot.send_message(call.message.chat.id, set_chat_msg)
        bot.register_next_step_handler(sent_set_chat_msg, set_start_date)


    @bot.message_handler(commands=['messages'])  # просмотр всех рассылок
    def set_request_text(message):
        set_request_msg = 'Введите текст рассылки:'
        sent_request_msg = bot.send_message( message.chat.id, set_request_msg, parse_mode='html')
        # bot.register_next_step_handler(sent_request_msg, set_start_date)


    def set_start_date(message):
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = [now.year, now.month]
        current_shown_dates[chat_id] = date  # Saving the current date in a dict

        requests[requests_count]['text'] = message.text

        markup = create_calendar(now.year, now.month)
        bot.send_message(message.chat.id, "Выберите дату начала:", reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: 'DAY' in call.data and 'ENDDAY' not in call.data)
    def get_day(call):
        chat_id = call.message.chat.id
        saved_date = current_shown_dates.get(chat_id)

        if saved_date is not None:
            day = call.data[11:] if ';' in call.data[10:11] else call.data[12:]
            date = datetime.datetime(int(saved_date[0]), int(saved_date[1]), int(day), 0, 0, 0).strftime("%d.%m.%Y")
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='ПОДТВЕРДИТЬ', callback_data='accept_data;' + str(date))
            keyboard.add(callback_button)
            callback_button = types.InlineKeyboardButton(text='ИЗМЕНИТЬ', callback_data='edit_data')
            keyboard.add(callback_button)
            bot.edit_message_text("Выбранная дата:\n" + str(date), call.from_user.id, call.message.message_id, reply_markup=keyboard)
            bot.answer_callback_query(call.id, text="")

        else:
            # add your reaction for shown an error
            pass


    def set_end_date(call):
        message = call.message
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = [now.year, now.month]
        current_shown_dates[chat_id] = date  # Saving the current date in a dict
        print(current_shown_dates)
        markup = create_end_calendar(now.year, now.month)
        bot.edit_message_text("Выберите дату окончания:", call.from_user.id, call.message.message_id, reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: 'ENDDAY' in call.data)
    def set_end_day(call):
        chat_id = call.message.chat.id
        saved_date = current_shown_dates.get(chat_id)
        if saved_date is not None:
            day = call.data[14:] if ';' in call.data[13:14] else call.data[15:]
            date = datetime.datetime(int(saved_date[0]), int(saved_date[1]), int(day), 0, 0, 0).strftime("%d.%m.%Y")
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='ПОДТВЕРДИТЬ', callback_data='accept_end_data;' + str(date))
            keyboard.add(callback_button)
            callback_button = types.InlineKeyboardButton(text='ИЗМЕНИТЬ', callback_data='edit_end_data')
            keyboard.add(callback_button)
            bot.edit_message_text("Выбранная дата окончания:\n" + str(date), call.from_user.id, call.message.message_id, reply_markup=keyboard)
            bot.answer_callback_query(call.id, text="")

        else:
            # add your reaction for shown an error
            pass


    @bot.callback_query_handler(func=lambda call: 'NEXT-MONTH' in call.data and 'NEXT-END-MONTH' not in call.data)
    def next_month(call):
        chat_id = call.message.chat.id
        saved_date = current_shown_dates.get(chat_id)
        if saved_date is not None:
            year,month = saved_date
            month += 1
            if month > 12:
                month = 1
                year += 1
            date = [year, month]
            current_shown_dates[chat_id] = date
            markup = create_calendar(year, month)
            bot.edit_message_text("Выберите дату:", call.from_user.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        else:
            # add your reaction for shown an error
            pass


    @bot.callback_query_handler(func=lambda call: 'NEXT-END-MONTH' in call.data)
    def previous_month(call):
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
            markup = create_end_calendar(year, month)
            bot.edit_message_text("Выберите дату окончания:", call.from_user.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        else:
            # add your reaction for shown an error
            pass


    @bot.callback_query_handler(func=lambda call: 'PREV-MONTH' in call.data and 'PREV-END-MONTH' not in call.data)
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


    @bot.callback_query_handler(func=lambda call: 'PREV-END-MONTH' in call.data)
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
            markup = create_end_calendar(year, month)
            bot.edit_message_text("Выберите дату окончания:", call.from_user.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        else:
            # add your reaction for shown an error
            pass


    @bot.callback_query_handler(func=lambda call: "IGNORE" in call.data)
    def ignore(call):
        bot.answer_callback_query(call.id, text="smth wrong")


    @bot.callback_query_handler(func=lambda call: call.data == "edit_data")
    def get_calendar(call):
        message = call.message
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = (now.year,now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict

        markup = create_calendar(now.year, now.month)
        bot.edit_message_text("Изменить дату:", call.from_user.id, call.message.message_id, reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: call.data == "edit_end_data")
    def get_calendar(call):
        message = call.message
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict

        markup = create_end_calendar(now.year, now.month)
        bot.edit_message_text("Изменить дату:", call.from_user.id, call.message.message_id, reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: "accept_data" in call.data and "accept_end_data" not in call.data)
    def get_calendar(call):
        choose_msg = 'Выберите период отправки сообщениий:'
        keyboard = types.InlineKeyboardMarkup()
        date = call.data[12:]
        requests[requests_count]['start_date'] = date
        period_buttons = [{'text': '1 день', 'callback': 'PERIOD;1'},
                          {'text': '2 дня', 'callback': 'PERIOD;2'},
                          {'text': '3 дня', 'callback': 'PERIOD;3'},
                          {'text': '4 дня', 'callback': 'PERIOD;4'},
                          {'text': '5 дней', 'callback': 'PERIOD;5'},
                          {'text': '6 дней', 'callback': 'PERIOD;6'},
                          {'text': '7 дней', 'callback': 'PERIOD;7'},
                          {'text': 'Выходные дни', 'callback': 'PERIOD;R'},
                          {'text': 'Будние дни', 'callback': 'PERIOD;W'},
                          {'text': 'Каждый конкретный день недели', 'callback': 'PERIOD;D'},
                          {'text': 'Каждое конкретное число месяца', 'callback': 'PERIOD;N'}]

        for btn in period_buttons:
            text, callback = btn['text'], btn['callback']
            callback_button = types.InlineKeyboardButton(text=text, callback_data=callback)
            keyboard.add(callback_button)

        bot.edit_message_text(choose_msg, call.from_user.id, call.message.message_id, reply_markup=keyboard)


    @bot.callback_query_handler(func=lambda call: 'accept_end_data' in call.data)
    def success(call):
        end_date = call.data[16:]
        requests[requests_count]['end_date'] = end_date
        print(requests)
        success_msg = "Рассылка создана."
        bot.edit_message_text(success_msg, call.from_user.id, call.message.message_id)
        # send_request(requests[requests_count])
        threads.append({})
        threads[requests_count]['target'] = send_request
        threads[requests_count]['name'] = "Request " + str(requests_count) + " thread"
        threads[requests_count]['args'] = requests[requests_count]
        print('args', threads[requests_count]['args'])
        threads[requests_count]['daemon'] = True
        new_request_thread = th.Thread(target=threads[requests_count]['target'], name=threads[requests_count]['name'], args=([threads[requests_count]['args']]), daemon=threads[requests_count]['daemon'])
        new_request_thread.start()


    @bot.callback_query_handler(func=lambda call: "PERIOD" in call.data)
    def set_period(call):
        period = call.data[7:8]
        chat_id = call.from_user.id
        message_id = call.message.message_id

        set_time(period, chat_id, message_id)


    def set_time(period, chat_id, message_id):

        if period[0] in [str(x) for x in range(1, 8)] or period[0] in 'RW':

            set_time_msg = "Выберите часы отправки:"
            markup = create_time()
            bot.edit_message_text(set_time_msg, chat_id, message_id, reply_markup=markup)
            # print(period)
            requests[requests_count]['period'] = period
            print('period from set_time', period)
            requests[requests_count]['period_opts'] = 'weekdays' if len(period) != 1 else 'every;' + str(period[0]) + ';day'
            print(requests)
            wright_period(period)

        elif period == 'D':

            set_weekdays_msg = "Выберите дни недели:"
            keyboard = types.InlineKeyboardMarkup()
            weekdays_buttons = [{'text': 'Mo', 'callback': 'WEEK;1;0'},
                              {'text': 'Tu', 'callback': 'WEEK;2;0'},
                              {'text': 'We', 'callback': 'WEEK;3;0'},
                              {'text': 'Th', 'callback': 'WEEK;4;0'},
                              {'text': 'Fr', 'callback': 'WEEK;5;0'},
                              {'text': 'Sa', 'callback': 'WEEK;6;0'},
                              {'text': 'Su', 'callback': 'WEEK;7;0'},
                              {'text': 'Подтвердить', 'callback': 'WEEK;A;0'},
                              {'text': 'Назад', 'callback': 'WEEK;B;0'}]

            for btn in weekdays_buttons:
                text, callback = btn['text'], btn['callback']
                callback_button = types.InlineKeyboardButton(text=text, callback_data=callback)
                keyboard.add(callback_button)
            # bot.edit_message_reply_markup(chat_id, message_id,)
            bot.edit_message_text(set_weekdays_msg, chat_id, message_id, reply_markup=keyboard)

        elif period == 'N':
            # сделать сюда такой же выбор как и в днях недели
            set_month_dates_msg = "Выберите числа месяца для отправки:"
            markup = create_month()
            bot.edit_message_text(set_month_dates_msg, chat_id, message_id, reply_markup=markup)

        elif period == 'month_day':
            pass


    def wright_period(period__):
        pass  # записываем период


    period = []


    @bot.callback_query_handler(func=lambda call: "DATE" in call.data)
    def set_date_number(call):
        set_end_date(call)


    @bot.callback_query_handler(func=lambda call: "WEEK" in call.data)
    def set_weekdays(call):
        chat_id = call.from_user.id
        message_id = call.message.message_id
        keyboard = types.InlineKeyboardMarkup()

        weekdays_buttons = [{'text': 'Mo', 'callback': 'WEEK;1;0'},
                            {'text': 'Tu', 'callback': 'WEEK;2;0'},
                            {'text': 'We', 'callback': 'WEEK;3;0'},
                            {'text': 'Th', 'callback': 'WEEK;4;0'},
                            {'text': 'Fr', 'callback': 'WEEK;5;0'},
                            {'text': 'Sa', 'callback': 'WEEK;6;0'},
                            {'text': 'Su', 'callback': 'WEEK;7;0'},
                            {'text': 'Подтвердить', 'callback': 'WEEK;A;0'},
                            {'text': 'Назад', 'callback': 'WEEK;B;0'}]

        if call.data[5:6] in [str(c) for c in range(1, 8)]:

            if call.data[7:] == '0':
                weekdays_buttons = tick_button(call, weekdays_buttons, "tick")
                period.append(call.data[5:6])

            elif call.data[7:] == '1':
                weekdays_buttons = tick_button(call, weekdays_buttons, "untick")
                period.remove(call.data[5:6])

            for btn in weekdays_buttons:
                text, callback = btn['text'], btn['callback']
                callback_button = types.InlineKeyboardButton(text=text, callback_data=callback)
                keyboard.add(callback_button)

            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)

        elif call.data[5:6] is "A":
            # записать выбранные дни
            print(period)
            set_time(period, chat_id, message_id)
        elif call.data[5:6] is "B":
            get_calendar(call)


    curr_weekdays_buttons = [{'text': 'Mo', 'callback': 'WEEK;1;0'},
                            {'text': 'Tu', 'callback': 'WEEK;2;0'},
                            {'text': 'We', 'callback': 'WEEK;3;0'},
                            {'text': 'Th', 'callback': 'WEEK;4;0'},
                            {'text': 'Fr', 'callback': 'WEEK;5;0'},
                            {'text': 'Sa', 'callback': 'WEEK;6;0'},
                            {'text': 'Su', 'callback': 'WEEK;7;0'},
                            {'text': 'Подтвердить', 'callback': 'WEEK;A;0'},
                             {'text': 'Назад', 'callback': 'WEEK;B;0'}]


    def tick_button(call, buttons, event):
        if event == "tick":
            for i in range(len(buttons)):
                btn = buttons[i]
                if call.data == btn['callback']:
                    buttons[i]['text'] = '✓ ' + btn['text']
                    buttons[i]['callback'] = 'WEEK;1;1'
                    curr_weekdays_buttons[i]['text'] = buttons[i]['text']
        elif event == "untick":
            for i in range(len(buttons)):
                btn = buttons[i]
                if call.data == btn['callback']:
                    buttons[i]['text'] = btn['text'][2:]
                    buttons[i]['callback'] = 'WEEK;1;0'
                    curr_weekdays_buttons[i]['text'] = buttons[i]['text']

        return curr_weekdays_buttons


    @bot.callback_query_handler(func=lambda call: "TIME" in call.data)
    def set_hour(call):
        time = call.data[5:7] if ';' not in call.data[5:7] else call.data[5:6]
        time = str(time) + ":00"
        print(time)
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text='ПОДТВЕРДИТЬ', callback_data='accept_time;' + time)
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='ИЗМЕНИТЬ', callback_data='edit_time')
        keyboard.add(callback_button)
        bot.edit_message_text("Выбранное время:\n" + time, call.from_user.id, call.message.message_id,
                              reply_markup=keyboard)


    @bot.callback_query_handler(func=lambda call: call.data == 'edit_time')
    def set_hour(call):
        markup = create_time()
        bot.edit_message_text("Изменить время:\n", call.from_user.id, call.message.message_id,
                              reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: 'accept_time' in call.data)
    def set_hour(call):
        time = call.data[12:]
        requests[requests_count]['time'] = time

        bot.edit_message_text("Время выбрано!", call.from_user.id, call.message.message_id)
        set_end_date(call)


    # def format_period(_period, period_opts):
    #     if "weekdays" in period_opts:
    #         for day in _period:

    def send_request_period(_period, curr_weekday, curr_datetime, curr_request, request_datetime):
        chat_id, text = curr_request['chat_id'], curr_request['text']

        for day in period:

            if day == curr_weekday and curr_datetime == request_datetime:
                print('all is ok (1)')
                response_message = bot.send_message(chat_id, text, parse_mode='html')
                bot.register_next_step_handler(response_message, get_response)

            elif curr_datetime < request_datetime:
                sleep(60)
                send_request(curr_request)


    def get_curr_request_date(curr_datetime, curr_request):

        start_date = curr_request['start_date'] + ' ' + curr_request['time']
        end_date = curr_request['end_date'] + ' ' + curr_request['time']
        print('start date', start_date)
        print('end date', end_date)
        print('curr date', curr_datetime)

        if start_date <= curr_datetime <= end_date:
            print('all is ok (2)')
            curr_datetime = curr_datetime

        elif curr_datetime <= start_date:
            sleep(1)
            get_curr_request_date(curr_datetime, curr_request)

        else:
            curr_datetime = None

        return curr_datetime


    def send_request(request):
        print(request)
        # request = request[requests_count]
        curr_request = deepcopy(request)
        print(request)
        print('current request:', curr_request)
        chat_id, text, start_date, period, period_opts, time, end_date = request['chat_id'], request['text'], request['start_date'], request['period'], request['period_opts'], request['time'], request['end_date']
        curr_datetime = str(datetime.datetime.now().strftime("%d.%m.%Y %H:") + "00")
        request_datetime = get_curr_request_date(curr_datetime, curr_request)
        curr_weekday = str(datetime.datetime.today().weekday())

        if "weekdays" in period_opts:
            send_request_period(period, curr_weekday, curr_datetime, curr_request, request_datetime)

        elif "every" in period_opts and period in [str(c) for c in range(1, 8)]:

            if period == curr_weekday and curr_datetime == request_datetime:
                response_message = bot.send_message(chat_id, text, parse_mode='html')
                bot.register_next_step_handler(response_message, get_response)

            elif curr_datetime <= request_datetime:
                sleep(1)
                send_request(curr_request)

        elif "every" in period_opts and period in "RW":
            if period == "R":
                period = ['6', '7']

                send_request_period(period, curr_weekday, curr_datetime, curr_request, request_datetime)

            elif period == "W":
                period = [str(c) for c in range(1, 6)]

                send_request_period(period, curr_weekday, curr_datetime, curr_request, request_datetime)


    def get_response(message):
        print(message.text)


    bot.polling()


import telebot
import datetime
from telebot import types
from time import sleep
from copy import deepcopy


def new_bot(user_token):
    pers_bot = telebot.TeleBot(user_token)
    chat_list = []
    chat_count = 0
    requests = []
    requests_count = 0

    def get_chat_list(message):
        if message.chat.type == "group":
            chat_list.append(message.chat)
        return chat_list

    def update_requests_count(event):
        if event == 'add':
            return requests_count + 1
        elif event == 'del':
            return requests_count - 1

    def update_chat_count():
        print(chat_count)
        return chat_count + 1

    def set_chat(chat):
        # @pers_bot.message_handler(content_types=['text'])
        # @pers_bot.callback_query_handler(func=lambda call: call.data)
        def set_curr_chat(call):
            # Если сообщение из чата с ботом
            print('im in handler help me pls')
            requests.append({})
            requests[requests_count]['chat'] = call.message.chat.id
            if call.data == chat.id:
                print('Кажется получается')
                set_chat = 'Введите текст запроса в ' + chat.title
                pers_bot.send_message(call.message.chat.id, set_chat, parse_mode='html')

        print('im here from', chat.title)
        update_requests_count('add')

        set_chat = 'Введите текст запроса в ' + chat.title
        set_request()

        return set_chat

    def set_request():

        set_time()

        @pers_bot.message_handler(content_types=['text'])
        def handle_request(message):
            requests.append({})
            requests[requests_count]['text'] = message.text

            msg = 'Когда отправить запрос? Напишите ответ в виде 24.01 02:10 или ' \
                      'можете написать только время, чтобы отправить сегодня'
            pers_bot.send_message(message.chat.id, msg, parse_mode='html')

    def set_time():
        set_period()

        @pers_bot.message_handler(content_types=['text'])
        def handle_time(message):
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

            pers_bot.send_message(message.chat.id, choose_msg, reply_markup=keyboard, parse_mode='html')

    def set_period():
        @pers_bot.callback_query_handler(func=lambda call: True)
        def set_curr_period(call):
            requests[requests_count]['period'] = call.message.text

            set_period_msg = 'Всё готово'
            pers_bot.send_message(call.message.chat.id, set_period_msg, parse_mode='html')

            send_request(requests[requests_count])

    def send_request(request):
        curr_request = deepcopy(request)
        print('current request:', curr_request)
        chat, text, time, period = request['chat'], request['text'], request['time'], request['period']
        curr_datetime = datetime.datetime.now().strftime("%m.%d %H:%M")
        curr_time = datetime.datetime.now().strftime("%H:%M")
        if curr_datetime == time or curr_time == time:
            pers_bot.send_message(chat, text, parse_mode='html')
        else:
            sleep(60)
            send_request(curr_request)

    @pers_bot.message_handler(commands=['start'])
    def handle_pers_bot_start(message):
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

        btns = []
        if message.chat.type == "private":
            for chat in chat_list:
                if chat.title not in btns:
                    btns.append(chat.title)
                    update_chat_count()
                    # callback_button = types.InlineKeyboardButton(text=chat.title, callback_data="set_chat")
                    # keyboard.add(callback_button)
            #     нужно как-то переписать callback

            # setted_chat_msg = set_chat(chat_list[chat_count])
            # pers_bot.send_message(message.chat.id, setted_chat_msg, parse_mode='html')
        callback_button = types.InlineKeyboardButton(text="УДАЛИТЬ ЗАПРОС", callback_data="del_req")
        keyboard.add(callback_button)
        # callback_button = types.InlineKeyboardButton(text="СПИСОК ЧАТОВ", callback_data="chat_list")
        # keyboard.add(callback_button)
        sent_message = pers_bot.send_message(message.chat.id, hello_msg, reply_markup=keyboard, parse_mode='html')
        # pers_bot.register_next_step_handler(message, set_chat(chat_list[0]))

    @pers_bot.callback_query_handler(func=lambda call: True)
    def callback_pers_bot_inline(call):
        print('im in handler')
        # Если сообщение из чата с ботом
        msg = 'Удалено'
        chat_list_msg = 'Списочек чатиков'
        set_chat = 'Введите текст запроса в '
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="СПИСОК ЧАТОВ", callback_data="chat_list")
        keyboard.add(callback_button)

        if call.message:
            if call.data == "del_req":
                pers_bot.send_message(call.message.chat.id, msg, parse_mode='html')
            elif call.data == "chat_list":
                pers_bot.send_message(call.message.chat.id, chat_list_msg, parse_mode='html')
            elif call.data == "set_chat":
                pers_bot.send_message(call.message.chat.id, set_chat, parse_mode='html')
            elif call.data == "chat":
                print(call.data.chat)

    @pers_bot.message_handler(commands=['new'])
    def handle_pers_bot_new(message):
        # curr_chat()
        pass

    # @pers_bot.callback_query_handler(func=lambda call: call.data)
    # def set_curr_chat(call):
    #     print(call.chat)
        # # Если сообщение из чата с ботом
        # print('im in handler help me pls')
        # requests.append({})
        # requests[requests_count]['chat'] = call.message.chat.id
        #
        # if call.data == chat.id:
        #     print('Кажется получается')
        #     set_chat = 'Введите текст запроса в ' + chat.title
        #     pers_bot.send_message(call.message.chat.id, set_chat, parse_mode='html')

    pers_bot.polling(none_stop=True)


def main():
    new_bot('YOUR-BOT-TOKEN')


if __name__ == "__main__":
    main()

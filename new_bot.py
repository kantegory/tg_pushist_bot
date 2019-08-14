import telebot
from telebot import types
from copy import deepcopy
from time import sleep
import datetime

telebot.apihelper.proxy = {'https': 'socks5://userproxy:password@ip:port'}
user_token = 'YOUR-BOT-TOKEN'

# pers_bot = telebot.TeleBot(user_token)
bot = telebot.TeleBot(user_token)

chat_list = []
chat_count = 0
requests = []
requests_count = 0


# все вспомогательные функции пойдут в utils
def set_language():
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
    elif response_message > 10000 :
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


if __name__ == "__main__":
    # pers_bot.polling(none_stop=True)
    bot.polling(none_stop=True)

import telebot
from telebot import types
from new_bot import new_bot
import threading as th
from googlesheets import create_sheet, create_new_list, set_sheets_value, get_sheets_value
from telegramcalendar import create_calendar
import datetime
from db_scripts import *
from time import sleep
from googletrans import Translator

telebot.apihelper.proxy = {'https': 'socks5://USERPROXY:PASSWORD@IP:PORT'}
token = 'TOKEN'
bot = telebot.TeleBot(token)
admin = ['alantsoff', 'kantegory']
threads_bot = []
main_bot_stat = []
users = []
payments = []
promos = []
requests = []
sent_requests = []
threads_check_payment = []
first_day = datetime.datetime.today().strftime('%d.%m.%Y')
start_time = datetime.datetime.now()


# init main stat google sheet
scopes = ['https://www.googleapis.com/auth/spreadsheets']
title = 'Статистика Пушиста'
sheet_list = {'users': 'Статистика пользователей', 'for_days': 'Статистика по дням', 'for_hours': 'Статистика по часам'}
main_bot_spreadsheet_id, spreadsheet_url, service = create_sheet(scopes, title)

create_new_list(main_bot_spreadsheet_id, service, sheet_list['users'])
users_head_values = ['id',	'@username',	'Дата регистрации',	'Боты',	'Кол-во запросов за последний месяц',
                     'Кол-во софрмированных запросов',	'Тариф', 'Кол-во оплат', 'Сумма оплат',	'Промокоды',
                     'Кол-во использованных промокодов', 'Рефералы', 'Когда закончится полный период']
set_sheets_value(
    service,
    main_bot_spreadsheet_id,
    '{}!A{}:M{}'.format(sheet_list['users'], 1, 1),
    users_head_values
)

create_new_list(main_bot_spreadsheet_id, service, sheet_list['for_days'])
for_days_head_values = ['Дата',	'Кол-во новых пользователей:', 'Кол-во оплат:',	'Кол-во использования промокодов:',
                        'Кол-во запросов созданных за сутки:', 'Кол-во запросов отправленных за сутки:']
set_sheets_value(
    service,
    main_bot_spreadsheet_id,
    '{}!A{}:F{}'.format(sheet_list['for_days'], 1, 1),
    for_days_head_values
)

create_new_list(main_bot_spreadsheet_id, service, sheet_list['for_hours'])
for_hours_head_values = ['Дата', 'Кол-во новых пользователей:', 'Кол-во оплат:', 'Кол-во использования промокодов:',
                         'Кол-во запросов созданных за час:', 'Кол-во запросов отправленных за час:']
set_sheets_value(
    service,
    main_bot_spreadsheet_id,
    '{}!A{}:F{}'.format(sheet_list['for_hours'], 1, 1),
    for_hours_head_values
)


def translate_to(language_code, msg):

    translator = Translator()
    translated_msg = translator.translate(msg, language_code, 'ru')

    return translated_msg.text


def init_bot_info(_new_bot):

    bot_info = {
        'bot_tg_id': str(_new_bot.get_me().id),
        'bot_username': '@' + str(_new_bot.get_me().username)
    }

    return bot_info


def set_user_info(user_tg_id, user_name, user_language, user_refer_name, user_registration_date):
    user_info = [{
        'user_tg_id': str(user_tg_id),
        'user_name': str(user_name),
        'user_language': str(user_language),
        'user_refer_name': str(user_refer_name),
        'user_registration_date': str(user_registration_date)
    }]

    user_add(user_info)


def set_bot_info(bot_tg_id, bot_username, user_id, _spreadsheet_url):

    bot_info = [{
        'bot_tg_id': bot_tg_id,
        'bot_username': bot_username,
        'user_id': user_id,
        'bot_stat': _spreadsheet_url
    }]

    bot_add(bot_info)


def get_stat_for_day(day=None):

    sleep(5)

    # collect stat data
    day = datetime.datetime.today().strftime('%d.%m.%Y') if day is None else day
    users_count = str(len(select_users()))
    payments_count = str(len(select_payments()))
    promos_count = str(len(select_promos_count()))
    requests_count = str(len(select_requests()))
    requests_count = str(len(select_requests()))

    interval = get_interval(first_day, day) + 2

    if interval == 2:

        ranges = sheet_list['for_days'] + '!A{}:F{}'.format(interval, interval)
        values = [day, users_count, payments_count, promos_count, requests_count, requests_count]

        set_sheets_value(service, main_bot_spreadsheet_id, ranges, values)

    elif interval > 2:

        ranges = sheet_list['for_days'] + '!A{}:F{}'.format(interval, interval)
        values = [day, '=B2-{}'.format(users_count), '=C2-{}'.format(payments_count),
                  '=D2-{}'.format(promos_count), '=E2-{}'.format(requests_count),
                  '=E2-{}'.format(requests_count)]

        set_sheets_value(service, main_bot_spreadsheet_id, ranges, values)

    sleep(86400)
    get_stat_for_day(datetime.datetime.today().strftime('%d.%m.%Y'))


def get_stat_for_hour(daytime=None):

    # collect the data
    day = datetime.datetime.today().strftime('%d.%m.%Y')
    daytime = datetime.datetime.today() if daytime is None else daytime
    users_count = len(select_users())
    payments_count = len(select_payments())
    promos_count = len(select_promos_count())
    requests_count = len(select_requests())
    requests_count = len(select_requests())

    interval = get_hour_interval(start_time, daytime) + 2
    print('hour interval', interval)

    if interval == 2:

        ranges = sheet_list['for_hours'] + '!A{}:F{}'.format(interval, interval)
        values = [day + ' ' + daytime.time().strftime('%H:%M'), users_count, payments_count, promos_count, requests_count, requests_count]

        set_sheets_value(service, main_bot_spreadsheet_id, ranges, values)

    elif interval > 2:

        ranges = sheet_list['for_hours'] + '!A{}:F{}'.format(interval, interval)
        values = [day + ' ' + daytime.strftime('%H:%M'), '=B2-{}'.format(users_count), '=C2-{}'.format(payments_count),
                  '=D2-{}'.format(promos_count), '=E2-{}'.format(requests_count),
                  '=E2-{}'.format(requests_count)]

        set_sheets_value(service, main_bot_spreadsheet_id, ranges, values)

    sleep(3600)
    get_stat_for_hour(datetime.datetime.today())


def get_stat_for_users():

    sleep(20)

    _users = select_users()

    for user in _users:

        user_tg_id = user['user_tg_id']
        user_name = user['user_name']
        user_bots = ', '.join([_bot['bot_name'] for _bot in select_bot_by_user_id(user_tg_id)])
        user_requests = len(select_request_by_user_id(user_tg_id))
        user_requests_for_last_month = ''
        user_promos_count = len(select_promos(user_tg_id))
        user_payments = select_payment(user_tg_id)

        user_payments_count = len(user_payments) - user_promos_count
        tariff = {0: 'Использует промокод', 249: '1 месяц', 635: '3 месяца', 1195: '6 месяцев', 2092: '12 месяцев', 4500: '36 месяцев'}
        user_tariff = ''
        user_payments_sum = 0
        user_promos = []
        user_refs = select_user_by_refer_name(user_name)
        user_refs_names = []
        user_payment_end_date = ''
        users_count = _users.index(user) + 2

        for payment in user_payments:

            payment_amount = int(payment['payment_amount']) if payment['payment_amount'] != '' else 0
            user_payment_end_date = payment['payment_end_date']
            user_promos.append(payment['promo_value'])
            user_payments_sum += payment_amount
            user_tariff = tariff[payment_amount]

        for ref in user_refs:

            user_refs_names.append(ref['user_name'])

        user_refs_names = ', '.join(user_refs_names)
        user_promos = ', '.join(user_promos)
        user_registration_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        print('count of users right now', users_count)
        ranges = sheet_list['users'] + '!A{}:M{}'.format(users_count, users_count)

        # собираем все данные для отправки в таблицу
        values = [user_tg_id, user_name, user_registration_date, user_bots, user_requests_for_last_month, user_requests,
                  user_tariff, user_payments_count, user_payments_sum, user_promos, user_promos_count, user_refs_names,
                  user_payment_end_date]

        # записываем всё в таблицу
        set_sheets_value(service, main_bot_spreadsheet_id, ranges, values)

    sleep(60)
    get_stat_for_users()


get_stat_for_day_thread = th.Thread(target=get_stat_for_day, daemon=True)
get_stat_for_day_thread.start()
get_stat_for_hour_thread = th.Thread(target=get_stat_for_hour, daemon=True)
get_stat_for_hour_thread.start()
get_stat_for_users_thread = th.Thread(target=get_stat_for_users, daemon=True)
get_stat_for_users_thread.start()


def get_hour_interval(start, end):

    interval = end - start
    print('interval in seconds', interval.seconds)
    return interval.seconds // 3600


def goto_profile(call=None, message=None):

    user_id = ''
    username = ''
    language_code = 'ru'

    if call is not None:

        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        user_id = call.from_user.id
        username = call.from_user.username
        language_code = call.from_user.language_code

    elif message is not None:

        bot.clear_step_handler_by_chat_id(message.chat.id)
        user_id = message.from_user.id
        username = message.from_user.username
        language_code = message.from_user.language_code

    print('this is language_code', language_code)
    bot_list = select_bot_by_user_id(user_id)
    print(bot_list)
    print(user_id)
    print(select_user(user_id))
    user_status = select_user(user_id)[0]['user_status']
    payments_end_date = select_payment(user_id)
    payment_end_date = 0

    for payment in payments_end_date:
        payment_end_date = payment['payment_end_date']

    if user_status == '0':
        user_status = translate_to(language_code, 'Неоплаченный')
    elif user_status == '1':
        user_status = translate_to(language_code, 'Оплачен до {}').format(payment_end_date)

    goto_profile_msg = 'Добро пожаловать в личный кабинет! \n' \
                       '\n' \
                       'Здесь ты найдешь информацию по оплате и своим приглашенным. \n ' \
                       '\n' \
                       'Сейчас твой статус: {} \n' \
                       '\n' \
                       'Твои боты: \n'.format(user_status)

    goto_profile_msg = translate_to(language_code, goto_profile_msg)

    for _bot in bot_list:
        
        goto_profile_msg += '\n{}\n'.format(_bot['bot_name'])

    markup = types.InlineKeyboardMarkup()

    create_new_bot_text = translate_to(language_code, 'Создать нового бота')
    callback_button = types.InlineKeyboardButton(text=create_new_bot_text, callback_data='NEW-BOT')
    markup.add(callback_button)

    if username in admin:

        create_new_promo_text = translate_to(language_code, 'Создать промокод')
        callback_button = types.InlineKeyboardButton(text=create_new_promo_text, callback_data='CREATE;PROMO')
        markup.add(callback_button)

        show_promo_list_text = translate_to(language_code, 'Посмотреть все промокоды')
        callback_button = types.InlineKeyboardButton(text=show_promo_list_text, callback_data='PROMOLIST')
        markup.add(callback_button)

    pay_text = translate_to(language_code, 'Оплата')
    callback_button = types.InlineKeyboardButton(text=pay_text, callback_data='PAY')
    markup.add(callback_button)
    ref_text = translate_to(language_code, 'Мои рефералы')
    callback_button = types.InlineKeyboardButton(text=ref_text, callback_data='REF')
    markup.add(callback_button)
    stat_text = translate_to(language_code, 'Статистика')
    callback_button = types.InlineKeyboardButton(text=stat_text, callback_data='STAT')
    markup.add(callback_button)
    help_text = translate_to(language_code, 'Справка')
    callback_button = types.InlineKeyboardButton(text=help_text, callback_data='HELP')
    markup.add(callback_button)

    if message is not None:

        bot.send_message(message.chat.id, goto_profile_msg, reply_markup=markup)

    elif call is not None:

        bot.edit_message_text(goto_profile_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.message_handler(commands=['start'])
def handle_start(message):
    # print('attention', datetime.datetime.fromtimestamp(message.date))
    user_language = message.from_user.language_code
    user_id = message.from_user.id
    user_name = message.from_user.username

    users.append({})
    users_count = len(users) - 1
    users[users_count]['user_tg_id'] = user_id
    users[users_count]['user_name'] = user_name
    users[users_count]['user_language'] = user_language
    users[users_count]['user_status'] = '0'
    users[users_count]['user_registration_date'] = datetime.datetime.now().strftime('%d.%m.%Y  %H:%M')

    check_user = select_user(user_id)

    if check_user:

        goto_profile(message=message)

    else:

        handle_start_msg = 'Я помогаю контролировать сотрудников через чаты. \n' \
                           '\n' \
                           'Напоминаю нужным людям в нужные дни о том, что им нужно делать. ' \
                           'Попробуй меня и напиши @alantsoff обо мне отзыв.\n' \
                           '\n' \
                           'Вас кто-то пригласил?'
        handle_start_msg = translate_to(user_language, handle_start_msg)

        markup = types.InlineKeyboardMarkup()
        set_refer_text = translate_to(user_language, 'Да')
        callback_button = types.InlineKeyboardButton(text=set_refer_text, callback_data='SET-REFER')
        markup.add(callback_button)
        new_bot_text = translate_to(user_language, 'Нет')
        callback_button = types.InlineKeyboardButton(text=new_bot_text, callback_data='NEW-BOT')
        markup.add(callback_button)

        sent_message = bot.send_message(message.chat.id, handle_start_msg, reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data == 'SET-REFER')
def handle_refer_query(call):

    language_code = call.from_user.language_code

    handle_refer_query_msg = 'Введите никнейм в телеграме того, кто Вас пригласил:'
    handle_refer_query_msg = translate_to(language_code, handle_refer_query_msg)

    markup = types.InlineKeyboardMarkup()

    new_bot_text = translate_to(language_code, 'Пропустить этот шаг')
    callback_button = types.InlineKeyboardButton(text=new_bot_text, callback_data='NEW-BOT')
    markup.add(callback_button)

    sent_message = bot.edit_message_text(handle_refer_query_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.register_next_step_handler(sent_message, set_refer)


def set_refer(message):

    language_code = message.from_user.language_code

    refer = message.text

    if '@' in refer:
        refer = refer[1:]

    # set_refer_msg = ''
    refer_user = select_user_by_name(refer)
    users_count = len(users) - 1
    users[users_count]['user_refer_name'] = refer if refer_user else ''

    markup = types.InlineKeyboardMarkup()

    if refer_user and refer_user[0]['user_name'] != users[users_count]['user_name']:

        set_refer_msg = translate_to(language_code, 'Отлично! Вам и Вашему другу {} начислен '
                                                    'бесплатный месяц подписки (при оплате от 1 месяца).')

        set_refer_msg = set_refer_msg.format(refer)

        set_user_info(users[users_count]['user_tg_id'], users[users_count]['user_name'],
                      users[users_count]['user_language'], users[users_count]['user_refer_name'],
                      users[users_count]['user_registration_date'])

        new_bot_text = translate_to(language_code, 'Продолжить')
        callback_button = types.InlineKeyboardButton(text=new_bot_text, callback_data='NEW-BOT')
        markup.add(callback_button)

    elif refer_user and refer_user[0]['user_name'] == users[users_count]['user_name']:

        set_refer_msg = translate_to(language_code, 'Нельзя использовать свой ник! Хотите изменить никнейм?')
        set_refer_msg = set_refer_msg

        set_refer_text = translate_to(language_code, 'Да')
        callback_button = types.InlineKeyboardButton(text=set_refer_text, callback_data='SET-REFER')
        markup.add(callback_button)
        new_bot_text = translate_to(language_code, 'Нет')
        callback_button = types.InlineKeyboardButton(text=new_bot_text, callback_data='NEW-BOT')
        markup.add(callback_button)

    else:

        set_refer_msg = translate_to(language_code, 'К сожалению, пользователь {} не найден. Хотите изменить никнейм?')
        set_refer_msg = set_refer_msg.format('@' + refer)

        set_refer_text = translate_to(language_code, 'Да')
        callback_button = types.InlineKeyboardButton(text=set_refer_text, callback_data='SET-REFER')
        markup.add(callback_button)
        new_bot_text = translate_to(language_code, 'Нет')
        callback_button = types.InlineKeyboardButton(text=new_bot_text, callback_data='NEW-BOT')
        markup.add(callback_button)

    bot.send_message(message.chat.id, set_refer_msg, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'NEW-BOT')
def handle_new_bot_query(call):

    language_code = call.from_user.language_code

    users_count = len(users) - 1
    users[users_count]['user_refer_name'] = ''
    user_add(users)

    handle_new_bot_query_msg = '1. Перейдите в бот @BotFather и создайте новый бот. \n' \
                               '2. После создания бота вы получите токен бота (выглядит вот так – ' \
                               '<code>123456:ABC-DEF1234gh...</code>) – ' \
                               'скопируйте его сюда и отправьте.'

    handle_new_bot_query_msg = translate_to(language_code, handle_new_bot_query_msg)

    sent_msg = bot.edit_message_text(handle_new_bot_query_msg, call.message.chat.id, call.message.message_id, parse_mode='html')
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    bot.register_next_step_handler(sent_msg, handle_token)


def handle_token(message):

    language_code = message.from_user.language_code

    bot.clear_step_handler_by_chat_id(message.chat.id)

    new_bot_token = message.text.split()[0]
    print(new_bot_token)
    print(len(new_bot_token))
    if len(new_bot_token) == 45:

        try:

            new_bot_info = init_bot_info(telebot.TeleBot(new_bot_token))
            print(new_bot_info)
            if new_bot_info:
                print('im in if and it very good')
                bot_tg_id = new_bot_info['bot_tg_id']
                bot_username = new_bot_info['bot_username']
                user_id = message.from_user.id

                # напишите свой gmail чтобы иметь доступ к гугл таблице
                _scopes = ['https://www.googleapis.com/auth/spreadsheets']
                _title = bot_username
                _sheet_title = translate_to(language_code, 'Рассылки')
                spreadsheet_id, _spreadsheet_url, _service = create_sheet(scopes, _title)
                create_new_list(spreadsheet_id, service, 'Рассылки')
                create_new_list(spreadsheet_id, service, 'Ответы на запросы бота')
                values = [
                    ['Текст рассылки', 'Ответ', 'Реакция'],
                    ['Сколько денег заработал?', '1000', 'Надо поднажать'],
                    ['Сколько денег заработал?', '5000', 'Неплохо'],
                    ['Сколько денег заработал?', '10000', 'Отлично продолжай в том же духе']
                ]
                print(values)
                ranges = '{}!A{}:C{}'.format('Рассылки', 1, 4)
                set_sheets_value(_service, spreadsheet_id, ranges, values)
                values = ['Дата и время ответа', 'Текст ответа', 'Username', 'Чат', 'Дата и время запроса', 'Запрос']
                ranges = '{}!A{}:F{}'.format('Ответы на запросы бота', 1, 1)
                set_sheets_value(_service, spreadsheet_id, ranges, values)
                ranges = '{}!A{}:C{}'.format('Рассылки', 2, 4)
                answers = get_sheets_value(service, spreadsheet_id, ranges)
                print('this is answers attention', answers)

                print('bot spreadsheet', spreadsheet_url)
                threads_bot.append({})
                threads_bot_count = len(threads_bot) - 1
                threads_bot[threads_bot_count]['target'] = new_bot
                threads_bot[threads_bot_count]['name'] = "Bot " + str(new_bot_info['bot_username']) + " thread"
                threads_bot[threads_bot_count]['args'] = new_bot_token, language_code, _service, spreadsheet_id
                threads_bot[threads_bot_count]['daemon'] = True

                new_bot_thread = th.Thread(target=threads_bot[threads_bot_count]['target'], name=threads_bot[threads_bot_count]['name'],
                                       args=(threads_bot[threads_bot_count]['args']), daemon=threads_bot[threads_bot_count]['daemon'])

                new_bot_thread.start()

                handle_token_success_msg = 'Бот {} успешно запущен!'.format(new_bot_info['bot_username'])
                bot.send_message(message.chat.id, handle_token_success_msg)

                set_bot_info(bot_tg_id, bot_username, user_id, _spreadsheet_url)

            goto_profile(message=message)

        except:
            print('im in except')
            handle_token_error_msg = 'Что-то не так с токеном, попробуйте перевыпустить его в @BotFather' \
                                     ' при помощи команды /revoke и пришлите мне новый!'

            handle_token_error_msg = translate_to(language_code, handle_token_error_msg)

            sent_msg = bot.send_message(message.chat.id, handle_token_error_msg)

            bot.register_next_step_handler(sent_msg, handle_token)

    else:
        print('im in else')
        handle_token_error_msg = 'Что-то не так с токеном, попробуйте перевыпустить его в @BotFather' \
                                 ' при помощи команды /revoke и пришлите мне новый!'

        handle_token_error_msg = translate_to(language_code, handle_token_error_msg)

        sent_msg = bot.send_message(message.chat.id, handle_token_error_msg)

        bot.register_next_step_handler(sent_msg, handle_token)


@bot.callback_query_handler(func=lambda call: call.data == 'PAY')
def handle_pay_query(call):

    language_code = call.from_user.language_code

    bot.clear_step_handler_by_chat_id(call.message.chat.id)

    handle_pay_query_msg = 'А можно не оплачивать :) \n' \
                           '\n' \
                           'Вы и ваш друг получите дополнительно по 1 месяцу расширенного доступа, ' \
                           'если ваш друг при регистрации введёт ваш никнейм и оплатит хотя бы один месяц.'

    handle_pay_query_msg = translate_to(language_code, handle_pay_query_msg)

    markup = types.InlineKeyboardMarkup()

    payment_promo_text = translate_to(language_code, 'Ввести промокод')
    callback_button = types.InlineKeyboardButton(text=payment_promo_text, callback_data='PAYMENT;PROMO')
    markup.add(callback_button)
    payment_1_text = translate_to(language_code, '1 месяц - скидка 0%')
    callback_button = types.InlineKeyboardButton(text=payment_1_text, callback_data='PAYMENT;1')
    markup.add(callback_button)
    payment_3_text = translate_to(language_code, '3 месяца - скидка 20%')
    callback_button = types.InlineKeyboardButton(text=payment_3_text, callback_data='PAYMENT;3')
    markup.add(callback_button)
    payment_6_text = translate_to(language_code, '6 месяцев - скидка 30%')
    callback_button = types.InlineKeyboardButton(text=payment_6_text, callback_data='PAYMENT;6')
    markup.add(callback_button)
    payment_12_text = translate_to(language_code, '12 месяцев - скидка 40%')
    callback_button = types.InlineKeyboardButton(text=payment_12_text, callback_data='PAYMENT;12')
    markup.add(callback_button)
    payment_36_text = translate_to(language_code, 'Безлимит')
    callback_button = types.InlineKeyboardButton(text=payment_36_text, callback_data='PAYMENT;36')
    markup.add(callback_button)
    back_profile_text = translate_to(language_code, 'Назад')
    callback_button = types.InlineKeyboardButton(text=back_profile_text, callback_data='BACK;PROFILE')
    markup.add(callback_button)

    bot.edit_message_text(handle_pay_query_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'PAYMENT' in call.data)
def handle_payment_query(call):

    language_code = call.from_user.language_code

    info = call.data.split(';')
    action = info[1]

    if action == '1':
        pay_action(call)

    elif action == '3':
        pay_action(call)

    elif action == '6':
        pay_action(call)

    elif action == '12':
        pay_action(call)

    elif action == '36':
        pay_action(call)

    elif action == 'PROMO':

        handle_payment_promo_query_msg = 'Введите промокод:'
        handle_payment_promo_query_msg = translate_to(language_code, handle_payment_promo_query_msg)

        markup = types.InlineKeyboardMarkup()

        pay_text = translate_to(language_code, 'Назад')
        callback_button = types.InlineKeyboardButton(text=pay_text, callback_data='PAY')
        markup.add(callback_button)

        sent_message = bot.edit_message_text(handle_payment_promo_query_msg, call.message.chat.id,
                                             call.message.message_id, reply_markup=markup)

        bot.register_next_step_handler(sent_message, pay_promo)


def pay_action(call):

    language_code = call.from_user.language_code

    provider_token = '381764678:TEST:11132'

    prices = {
        '1': [types.LabeledPrice(translate_to(language_code, '1 месяц'), 24900)],
        '3': [types.LabeledPrice(translate_to(language_code, '3 месяца'), 63500)],
        '6': [types.LabeledPrice(translate_to(language_code, '6 месяцев'), 119500)],
        '12': [types.LabeledPrice(translate_to(language_code, '12 месяцев'), 209200)],
        '36': [types.LabeledPrice(translate_to(language_code, 'Безлимит'), 450000)]
    }

    action = call.data.split(sep=';')[1]

    description = {
        '1': translate_to(language_code, '1 месяц'),
        '3': translate_to(language_code, '3 месяца'),
        '6': translate_to(language_code, '6 месяцев'),
        '12': translate_to(language_code, '12 месяцев'),
        '36': translate_to(language_code, 'Безлимит (36 месяцев)')
    }

    _title = {
        '1': translate_to(language_code, '1 месяц'),
        '3': translate_to(language_code, '3 месяца'),
        '6': translate_to(language_code, '6 месяцев'),
        '12': translate_to(language_code, '12 месяцев'),
        '36': translate_to(language_code, 'Безлимит (36 месяцев)')
    }

    bot.clear_step_handler_by_chat_id(call.message.chat.id)

    bot.edit_message_text(translate_to(language_code, 'Оплатите {}').format(title[action]), call.message.chat.id, call.message.message_id)

    bot.send_invoice(call.message.chat.id, title='{}'.format(_title[action]),
                     description='{}'.format(description[action]),
                     provider_token=provider_token,
                     currency='RUB',
                     # photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
                     # photo_height=512,  # !=0/None or picture won't be shown
                     # photo_width=512,
                     # photo_size=512,
                     # is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices[action],
                     start_parameter='time-machine-example',
                     invoice_payload='{}'.format(call.from_user.id))


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    language_code = pre_checkout_query.from_user.language_code
    checkout_error_msg = translate_to(language_code, 'Что-то пошло не так, попробуйте ещё раз')
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message=checkout_error_msg)


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    print(message.successful_payment)
    language_code = message.from_user.language_code
    user_tg_id = str(message.from_user.id)

    curr_user_payments = select_payment(user_tg_id)

    last_payment_end_date = None

    if curr_user_payments:

        for _payment in curr_user_payments:

            last_payment_end_date = _payment['payment_end_date']

    curr_date = last_payment_end_date if last_payment_end_date is not None else datetime.datetime.now().strftime('%d.%m.%Y')

    got_payment_msg = translate_to(language_code, 'Оплата прошла успешно')

    bot.send_message(message.chat.id, got_payment_msg)

    payments.append({})
    payments_count = len(payments) - 1
    payments[payments_count]['payment_amount'] = str(message.successful_payment.total_amount // 100)
    payments[payments_count]['user_id'] = user_tg_id

    months = {'249': '1', '635': '3', '1195': '6', '2092': '12', '4500': '36'}

    payment_end_date = [curr_date.split(sep='.')[0],
                                 str(int(curr_date.split(sep='.')[1]) +
                                     int(months[payments[payments_count]['payment_amount']])),
                                 curr_date.split(sep='.')[2]]

    amount = int(months[payments[payments_count]['payment_amount']])

    payment_end_date = correct_payment_end_date(payment_end_date, amount)
    print('end_date_payment', payment_end_date)

    payments[payments_count]['payment_end_date'] = payment_end_date
    payments[payments_count]['promo_value'] = ''

    # обновляем данные в бд
    payment_add(payments)
    update_user_status(user_tg_id, '1')

    # запускаем ежедневную проверку оплаты
    set_check_payment_thread(user_tg_id)


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return (next_month - datetime.timedelta(days=next_month.day)).day


def correct_payment_end_date(payment_end_date, amount):

    curr_date = datetime.datetime.now().strftime('%d.%m.%Y')
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    last_day = last_day_of_month(datetime.date(year, month, 1))

    if int(payment_end_date[1]) > 12:

        while int(payment_end_date[1]) > 12:

            payment_end_date = [curr_date.split(sep='.')[0],
                                str(int(curr_date.split(sep='.')[1]) +
                                    amount - 12),
                                str(int(curr_date.split(sep='.')[2]) + 1)]

            amount -= 12

        return '.'.join(payment_end_date)

    elif int(payment_end_date[0]) > last_day:

        while int(payment_end_date[0]) > last_day:

            payment_end_date = [str(1), str(int(curr_date.split(sep='.')[1]) + 1), curr_date.split(sep='.')[2]]
            amount = 1

            if int(payment_end_date[1]) > 12:

                payment_end_date = [str(1), str(int(curr_date.split(sep='.')[1]) + amount - 12),
                                    str(int(curr_date.split(sep='.')[2]) + 1)]

        return '.'.join(payment_end_date)

    else:

        return '.'.join(payment_end_date)


def set_check_payment_thread(user_tg_id):

    threads_check_payment.append({})
    threads_check_payment_count = len(threads_check_payment) - 1
    threads_check_payment[threads_check_payment_count]['target'] = check_payment
    threads_check_payment[threads_check_payment_count]['name'] = "Check payment for {} thread".format(user_tg_id)
    threads_check_payment[threads_check_payment_count]['args'] = user_tg_id
    threads_check_payment[threads_check_payment_count]['daemon'] = True

    new_check_payment_thread = th.Thread(
        target=threads_check_payment[threads_check_payment_count]['target'],
        name=threads_check_payment[threads_check_payment_count]['name'],
        args=([threads_check_payment[threads_check_payment_count]['args']]),
        daemon=threads_check_payment[threads_check_payment_count]['daemon']
    )

    new_check_payment_thread.start()


def pay_promo(message):

    bot.clear_step_handler_by_chat_id(message.chat.id)

    language_code = message.from_user.language_code

    promolist = select_promo()
    user_promo = message.text.split()[0]
    curr_date = datetime.datetime.now().strftime('%d.%m.%Y')
    user_tg_id = str(message.from_user.id)

    if promolist:

        for _promo in promolist:

            if _promo['promo_value'] == user_promo and curr_date <= _promo['promo_end_date']:

                pay_promo_msg = translate_to(language_code, 'Промокод {} успешно активирован! '
                                                            'Вам доступно {} недель пользования ботом.')

                pay_promo_msg = pay_promo_msg.format(_promo['promo_value'], _promo['promo_action'])

                bot.send_message(message.chat.id, pay_promo_msg)

                # записываем в оплату
                payments.append({})
                payments_count = len(payments) - 1
                payments[payments_count]['payment_amount'] = ''
                payments[payments_count]['user_id'] = user_tg_id
                payment_end_date = [str(int(curr_date.split(sep='.')[0]) + int(_promo['promo_value']) * 7),
                                             curr_date.split(sep='.')[1], curr_date.split(sep='.')[2]]

                amount = int(_promo['promo_value']) * 7
                payment_end_date = correct_payment_end_date(payment_end_date, amount)

                payments[payments_count]['payment_end_date'] = payment_end_date
                payments[payments_count]['promo_value'] = _promo['value']

                payment_add(payments)
                update_user_status(user_tg_id, '1')

                # запускаем ежедневную проверку оплаты
                set_check_payment_thread(user_tg_id)

            elif curr_date > _promo['promo_end_date']:

                pay_promo_msg = translate_to(language_code, 'Срок действия промокода {}  истёк.')
                pay_promo_msg = pay_promo_msg.format(_promo['promo_value'])

                bot.send_message(message.chat.id, pay_promo_msg)

            else:

                pay_promo_msg = translate_to(language_code, 'Промокода {} не существует.')
                pay_promo_msg = pay_promo_msg.format(_promo['promo_value'])

                bot.send_message(message.chat.id, pay_promo_msg)


def check_payment(user_id):

    language_code = select_user(user_id)[0]['language_code']

    curr_date = datetime.datetime.now().strftime('%d.%m.%Y')
    payment = select_payment(int(user_id))

    if payment:

        payment_by_user_id = payment[0]
        end_date = payment_by_user_id['payment_end_date']

        interval = get_interval(curr_date, end_date)

        check_payment_msg = translate_to(language_code, 'До конца действия подписки осталось {} дней.')
        check_payment_msg = check_payment_msg.format(interval)
        markup = types.InlineKeyboardMarkup()

        pay_text = translate_to(language_code, 'Оплатить сейчас')
        callback_button = types.InlineKeyboardButton(text=pay_text, callback_data='PAY')
        markup.add(callback_button)

        if curr_date < end_date and interval > 7:

            sleep(86400)
            check_payment(user_id)

        elif curr_date < end_date and interval == 7:

            check_pay_text = translate_to(language_code, 'Напомнить позже')
            callback_button = types.InlineKeyboardButton(text=check_pay_text, callback_data='CHECK;PAY')
            markup.add(callback_button)

            bot.send_message(user_id, check_payment_msg, reply_markup=markup)

        elif curr_date < end_date and interval == 3:

            check_pay_text = translate_to(language_code, 'Напомнить позже')
            callback_button = types.InlineKeyboardButton(text=check_pay_text, callback_data='CHECK;PAY')
            markup.add(callback_button)

            bot.send_message(user_id, check_payment_msg, reply_markup=markup)

        elif curr_date < end_date and interval == 1:

            bot.send_message(user_id, check_payment_msg, reply_markup=markup)

        elif curr_date == end_date:

            check_payment_msg = translate_to(language_code, 'Подписка закончилась')

            markup = types.InlineKeyboardMarkup()

            pay_text = translate_to(language_code, 'Оплатить сейчас')
            callback_button = types.InlineKeyboardButton(text=pay_text, callback_data='PAY')
            markup.add(callback_button)

            update_user_status(user_id, '0')

            bot.send_message(user_id, check_payment_msg, reply_markup=markup)


def get_interval(start, end):
    print(end)
    start = start.split(sep='.')
    start = [int(c) for c in start]
    start = datetime.datetime(start[2], start[1], start[0])

    end = end.split(sep='.')
    end = [int(c) for c in end]
    end = datetime.datetime(end[2], end[1], end[0])

    interval = end - start

    return interval.days


@bot.callback_query_handler(func=lambda call: call.data == 'CHECK;PAY')
def handle_check_pay_query(call):

    user_id = call.from_user.id
    sleep(86400)
    check_payment(user_id)


@bot.callback_query_handler(func=lambda call: 'CREATE' in call.data)
def handle_create_query(call):

    language_code = call.from_user.language_code

    info = call.data.split(sep=';')
    action = info[1]

    if action == 'PROMO':

        handle_create_promo_query_msg = translate_to(language_code, 'Введите промокод:')

        markup = types.InlineKeyboardMarkup()

        back_profile_text = translate_to(language_code, 'Назад')
        callback_button = types.InlineKeyboardButton(text=back_profile_text, callback_data='BACK;PROFILE')
        markup.add(callback_button)

        sent_msg = bot.edit_message_text(handle_create_promo_query_msg, call.message.chat.id, call.message.message_id,
                                         reply_markup=markup)

        bot.register_next_step_handler(sent_msg, set_promo_value)


def set_promo_value(message):

    language_code = message.from_user.language_code

    promos.append({})
    promos_count = len(promos) - 1
    promos[promos_count]['promo_value'] = message.text

    set_promo_start_date_msg = translate_to(language_code, 'Выберите дату начала действия промокода: \n')

    markup = create_calendar(callback_info='START')

    bot.send_message(message.chat.id, set_promo_start_date_msg, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'DAY' in call.data)
def handle_date_query(call):

    language_code = call.from_user.language_code

    info = call.data.split(';')
    callback_info = info[0].split('-')[0]
    year, month, day = info[1], info[2], info[3]
    date = '{}.{}.{}'.format(day, month, year)

    handle_date_query_msg = translate_to(language_code, 'Выбранная дата: {}').format(date)

    markup = types.InlineKeyboardMarkup()
    accept_text = translate_to(language_code, 'Подтвердить')
    callback_button = types.InlineKeyboardButton(text=accept_text,
                                                 callback_data=callback_info + '-ACCEPT;' + date)
    markup.add(callback_button)
    edit_text = translate_to(language_code, 'Изменить')
    callback_button = types.InlineKeyboardButton(text=edit_text, callback_data=callback_info + '-EDIT')
    markup.add(callback_button)

    bot.edit_message_text(handle_date_query_msg, call.message.chat.id, call.message.message_id,
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'MONTH' in call.data)
def handle_month_query(call):

    language_code = call.from_user.language_code

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

    opt_msg = translate_to(language_code, 'начала') if callback_info == 'START' \
        else translate_to(language_code, 'окончания')

    handle_month_query_msg = translate_to(language_code, 'Выберите дату {}: \n').format(opt_msg)

    markup = create_calendar(year, month, callback_info)

    bot.edit_message_text(handle_month_query_msg, call.message.chat.id, call.message.message_id,
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'ACCEPT' in call.data)
def handle_date_accept_query(call):

    language_code = call.from_user.language_code

    info = call.data.split(';')
    callback_info = info[0].split('-')[0]
    date = info[1]

    promos_count = len(promos) - 1
    promos[promos_count]['promo_{}_date'.format(callback_info.lower())] = date

    handle_date_accept_query_msg = translate_to(language_code, 'Дата выбрана!')

    bot.answer_callback_query(call.id, text=handle_date_accept_query_msg)

    if callback_info == 'START':

        set_promo_action(call)

    elif callback_info == 'END':

        handle_date_accept_query_msg = translate_to(language_code, 'Промокод создан!')

        promo_add(promos)

        bot.edit_message_text(handle_date_accept_query_msg, call.message.chat.id, call.message.message_id)

        goto_profile(call=call)


def set_promo_action(call):

    language_code = call.from_user.language_code

    set_promo_action_msg = translate_to(language_code, 'Что даёт промокод?')

    markup = types.InlineKeyboardMarkup()

    promoaction_1_text = translate_to(language_code, '1 неделя')
    callback_button = types.InlineKeyboardButton(text=promoaction_1_text, callback_data='PROMOACTION;1')
    markup.add(callback_button)
    promoaction_2_text = translate_to(language_code, '2 недели')
    callback_button = types.InlineKeyboardButton(text=promoaction_2_text, callback_data='PROMOACTION;2')
    markup.add(callback_button)
    promoaction_4_text = translate_to(language_code, '1 месяц')
    callback_button = types.InlineKeyboardButton(text=promoaction_4_text, callback_data='PROMOACTION;4')
    markup.add(callback_button)

    bot.edit_message_text(set_promo_action_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'PROMOACTION' in call.data)
def handle_promo_action_query(call):

    language_code = call.from_user.language_code

    info = call.data.split(sep=';')
    action = info[1]

    promos_count = len(promos) - 1
    promos[promos_count]['promo_action'] = action

    handle_promo_action_query_msg = translate_to(language_code, 'Выберите дату окончания:\n')

    markup = create_calendar(callback_info='END')

    bot.edit_message_text(handle_promo_action_query_msg, call.message.chat.id,
                          call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'PROMOLIST')
def handle_promolist_query(call):

    language_code = call.from_user.language_code

    bot.clear_step_handler_by_chat_id(call.message.chat.id)

    promolist = select_promo()
    handle_promolist_query_msg = translate_to(language_code, 'Промокодов ещё не создано.')
    markup = types.InlineKeyboardMarkup()
    print('promolist', promolist)

    if promolist:

        handle_promolist_query_msg = translate_to(language_code, 'Выберите промокод, данные о котором хотите посмотреть:')

        for promo in promolist:
            print(promo)
            callback_button = types.InlineKeyboardButton(
                text='{}'.format(promo['promo_value']),
                callback_data='PROMOSHOW;{}'.format(promo['promo_id'])
            )
            markup.add(callback_button)

    back_profile_text = translate_to(language_code, 'Назад')
    callback_button = types.InlineKeyboardButton(text=back_profile_text, callback_data='BACK;PROFILE')
    markup.add(callback_button)

    bot.edit_message_text(handle_promolist_query_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'PROMOSHOW' in call.data)
def handle_promoshow_query(call):

    language_code = call.from_user.language_code

    info = call.data.split(sep=';')
    promo_id = int(info[1])

    promo = select_promo_by_id(promo_id)

    for _promo in promo:

        handle_promoshow_query_msg = 'Промокод: {}\n' \
                                     'Дата начала: {}\n' \
                                     'Даёт {} недель \n' \
                                     'Дата конца: {}'

        handle_promoshow_query_msg = translate_to(language_code, handle_promoshow_query_msg).format(
            _promo['promo_value'], _promo['promo_start_date'],
            _promo['promo_action'], _promo['promo_end_date'])

        markup = types.InlineKeyboardMarkup()

        promodel_text = translate_to(language_code, 'Удалить')
        callback_button = types.InlineKeyboardButton(text=promodel_text, callback_data='PROMODEL;{}'.format(promo_id))
        markup.add(callback_button)
        promolist_text = translate_to(language_code, 'Назад')
        callback_button = types.InlineKeyboardButton(text=promolist_text, callback_data='PROMOLIST')
        markup.add(callback_button)

        bot.edit_message_text(handle_promoshow_query_msg, call.message.chat.id,
                              call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'PROMODEL' in call.data)
def handle_promodel_query(call):

    language_code = call.from_user.language_code

    info = call.data.split(sep=';')

    promo_id = int(info[1])
    delete_promo(promo_id)
    promodel_success_text = translate_to(language_code, 'Промокод успешно удалён!')
    bot.answer_callback_query(call.id, text=promodel_success_text)

    promolist = select_promo()
    handle_promolist_query_msg = translate_to(language_code, 'Промокодов пока нет')

    markup = types.InlineKeyboardMarkup()
    if promolist:

        handle_promolist_query_msg = 'Выберите промокод, данные о котором хотите посмотреть:'
        handle_promolist_query_msg = translate_to(language_code, handle_promolist_query_msg)

        for promo in promolist:
            callback_button = types.InlineKeyboardButton(
                text='{}'.format(promo['promo_value']), callback_data='PROMOSHOW;{}'.format(promo['promo_id']))
            markup.add(callback_button)

    back_profile_text = translate_to(language_code, 'Назад')
    callback_button = types.InlineKeyboardButton(text=back_profile_text, callback_data='BACK;PROFILE')
    markup.add(callback_button)

    bot.edit_message_text(handle_promolist_query_msg, call.message.chat.id, call.message.message_id,
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'BACK' in call.data)
def handle_back_query(call):

    bot.clear_step_handler_by_chat_id(call.message.chat.id)

    info = call.data.split(sep=';')
    state = info[1]

    if state == 'PROFILE':

        goto_profile(call=call)


@bot.callback_query_handler(func=lambda call: call.data == 'REF')
def handle_ref_query(call):

    language_code = call.from_user.language_code

    ref_list = select_user_by_refer_name(call.from_user.username)

    handle_ref_query_msg = translate_to(language_code, 'Ваши рефералы:')

    markup = types.InlineKeyboardMarkup()

    back_profile_text = translate_to(language_code, 'Назад')
    callback_button = types.InlineKeyboardButton(text=back_profile_text, callback_data='BACK;PROFILE')
    markup.add(callback_button)


    if ref_list:

        for refer in ref_list:

            handle_ref_query_msg += '\n@{}\n'.format(refer['user_name'])
    else:

        handle_ref_query_msg = translate_to(language_code, 'Вы ещё никого не пригласили.')

    bot.edit_message_text(handle_ref_query_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'HELP')
def handle_help_query(call):

    language_code = call.from_user.language_code

    handle_help_query_msg = 'Инструкция по ссылке: https://clck.ru/H8HeE \n' \
                            '\n' \
                            'Открытый чат для общения и решения вопросов: \n' \
                            'https://t.me/joinchat/AAGeRBZPliIGwdcIcmqM0Q \n' \
                            '\n' \
                            'Если будут серьезные вопросы, пишите мне напрямую @alantsoff'
    handle_help_query_msg = translate_to(language_code, handle_help_query_msg)

    markup = types.InlineKeyboardMarkup()

    back_profile_text = translate_to(language_code, 'Назад')
    callback_button = types.InlineKeyboardButton(text=back_profile_text, callback_data='BACK;PROFILE')
    markup.add(callback_button)

    bot.edit_message_text(handle_help_query_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'STAT')
def handle_stat_query(call):

    language_code = call.from_user.language_code

    handle_stat_query_msg = translate_to(language_code, 'Выберите бота, для которого хотите посмотреть статистику:')

    bot_list = select_bot_by_user_id(call.from_user.id)
    markup = types.InlineKeyboardMarkup()

    stat_spreadsheet = spreadsheet_url

    if call.from_user.username in admin:

        callback_button = types.InlineKeyboardButton(text='{}'.format(bot.get_me().username),
                                                     url='{}'.format(stat_spreadsheet))
        markup.add(callback_button)

    if bot_list:
        print(bot_list)
        for _bot in bot_list:
            print('this is bad url???? {}'.format(_bot['bot_stat']))
            callback_button = types.InlineKeyboardButton(text='{}'.format(_bot['bot_name']),
                                                         url='{}'.format(_bot['bot_stat']))
            markup.add(callback_button)
    else:

        handle_stat_query_msg = translate_to(language_code, 'Ботов нет :(')

    back_profile_text = translate_to(language_code, 'Назад')
    callback_button = types.InlineKeyboardButton(text=back_profile_text, callback_data='BACK;PROFILE')
    markup.add(callback_button)

    bot.edit_message_text(handle_stat_query_msg, call.message.chat.id, call.message.message_id, reply_markup=markup)


bot.polling(none_stop=True)

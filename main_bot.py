import telebot
from telebot import types

token = 'YOUR-BOT-TOKEN'
bot = telebot.TeleBot(token)
telebot.apihelper.proxy = {'https': 'socks5://userproxy:password@ip:port'}


threads_bot = []
main_bot_stat = []
users = []
payments = []
promos = []
requests = []
sent_requests = []


def get_stat_for_today():
    today = datetime.datetime.today().strftime('%d.%m.%Y')
    main_bot_stat.append({})
    main_bot_stat_count = len(main_bot_stat) - 1
    users_count = len(users) - 1
    payments_count = len(users) - 1
    promos_count = len(promos) - 1
    requests_count = len(requests) - 1
    sent_requests_count = len(sent_requests) - 1

    main_bot_stat[main_bot_stat_count]['day'] = today
    main_bot_stat[main_bot_stat_count]['users_count'] = users_count
    main_bot_stat[main_bot_stat_count]['payments_count'] = payments_count
    main_bot_stat[main_bot_stat_count]['promos_count'] = promos_count
    main_bot_stat[main_bot_stat_count]['requests_count'] = requests_count
    main_bot_stat[main_bot_stat_count]['sent_requests_count'] = sent_requests_count


@bot.message_handler(commands=['start'])
def handle_start(message):
    language = message.from_user.language_code
    user_id = message.from_user.id
    username = message.from_user.username

    users.append({})
    users_count = len(users) - 1
    users[users_count]['user_id'] = user_id
    users[users_count]['username'] = username
    users[users_count]['language'] = language

    hello_msg = "Я помогаю контролировать сотрудников через чаты. \n" \
                "\n" \
                "Напоминаю нужным людям в нужные дни о том, что им нужно делать. " \
                "Попробуй меня и напиши @alantsoff обо мне отзыв."
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="ПОЕХАЛИ", callback_data="newbot")
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text="ВВЕСТИ НИКНЕЙМ ТОГО, КТО ВАС ПРИГЛАСИЛ", callback_data="set_refer")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, hello_msg, reply_markup=keyboard, parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data == 'newbot')
def callback_inline(call):
    msg = '1. Перейдите в бот @BotFather и создайте новый бот. \n' \
          '2. После создания бота вы получите токен бота (выглядит вот так – ' \
          '<code>123456:ABC-DEF1234gh...</code>) – ' \
          'скопируйте его сюда и отправьте.'

    sent_msg = bot.send_message(call.message.chat.id, msg, parse_mode='html')
    bot.register_next_step_handler(sent_msg, handle_token)


@bot.message_handler(commands=['cab'])
def personal(message):
    msg = 'Добро пожаловать в личный кабинет! \n' \
          '\n' \
          'Здесь ты найдешь информацию по оплате и своим приглашенным. \n ' \
          '\n' \
          'Сейчас твой статус: 🚫 Неоплаченный \n' \
          '\n' \
          'Твой бот:'
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='ОПЛАТА', callback_data='payment')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='МОИ РЕФЕРАЛЫ', callback_data='refer')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='ВВЕСТИ ПРОМОКОД', callback_data='promo')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='СТАТИСТИКА', callback_data='stat')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='СПРАВКА', callback_data='help')
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'cab')
def personal_from_callback(call):
    message = call.message
    msg = 'Добро пожаловать в личный кабинет! \n' \
          '\n' \
          'Здесь ты найдешь информацию по оплате и своим приглашенным. \n ' \
          '\n' \
          'Сейчас твой статус: 🚫 Неоплаченный \n' \
          '\n' \
          'Твой бот:'
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='МОИ РАССЫЛКИ', callback_data='requests')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='ОПЛАТА', callback_data='payment')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='МОИ РЕФЕРАЛЫ', callback_data='refer')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='ВВЕСТИ ПРОМОКОД', callback_data='promo')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='СТАТИСТИКА', callback_data='stat')
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='СПРАВКА', callback_data='help')
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'payment' in call.data)
def callback_inline(call):
    user_id = str(call.message.from_user.id)
    print(user_id)
    payments.append({})
    payments_count = len(users) - 1
    payments[payments_count]['user_id'] = user_id
    payments[payments_count]['username'] = str(call.message.from_user.username)

    if call.data[7:]:
        sub = call.data[8:]
        sub_months = sub[0:2] if "_" not in sub[0:2] else sub[0:1]
        print(sub_months)
        if sub_months == '1':
            price = '249'
            payments[payments_count]['price'] = price
            msg = 'Нажмите на кнопку для оплаты. ' \
                  'Ссылка действительна 30 минут.' \
                  'Не меняйте комментарий при оплате. ' \
                  'После ее совершения вам придет сообщение об открытии полного функционала бота.'
            qiwi_pay_url = 'https://qiwi.com/payment/form/99?amountFraction=0.0&currency=RUB&extra%5B%27account%27%5D=79258550898&extra%5B%27comment%27%5D=' + user_id + '&amountInteger=' + price
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='Перейти к оплате', callback_data='payment_success',
                                                         url=qiwi_pay_url)
            keyboard.add(callback_button)
            callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
            keyboard.add(callback_button)
            bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)
        elif sub_months == '3':
            price = '597.6'

            payments[payments_count]['price'] = price
            msg = 'Нажмите на кнопку для оплаты. ' \
                  'Ссылка действительна 30 минут.' \
                  'Не меняйте комментарий при оплате. ' \
                  'После ее совершения вам придет сообщение об открытии полного функционала бота.'
            qiwi_pay_url = 'https://qiwi.com/payment/form/99?amountFraction=0.0&currency=RUB&extra%5B%27account%27%5D=79258550898&extra%5B%27comment%27%5D=' + user_id + '&amountInteger=' + price
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='Перейти к оплате', callback_data='payment_success',
                                                         url=qiwi_pay_url)
            keyboard.add(callback_button)
            callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
            keyboard.add(callback_button)
            bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)
        elif sub_months == '6':
            price = '1045.8'

            payments[payments_count]['price'] = price
            msg = 'Нажмите на кнопку для оплаты. ' \
                  'Ссылка действительна 30 минут.' \
                  'Не меняйте комментарий при оплате. ' \
                  'После ее совершения вам придет сообщение об открытии полного функционала бота.'
            qiwi_pay_url = 'https://qiwi.com/payment/form/99?amountFraction=0.0&currency=RUB&extra%5B%27account%27%5D=79258550898&extra%5B%27comment%27%5D=' + user_id + '&amountInteger=' + price
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='Перейти к оплате', callback_data='payment_success',
                                                         url=qiwi_pay_url)
            keyboard.add(callback_button)
            callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
            keyboard.add(callback_button)
            bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)
        elif sub_months == '12':
            price = '1792.8'

            payments[payments_count]['price'] = price
            msg = 'Нажмите на кнопку для оплаты. ' \
                  'Ссылка действительна 30 минут.' \
                  'Не меняйте комментарий при оплате. ' \
                  'После ее совершения вам придет сообщение об открытии полного функционала бота.'
            qiwi_pay_url = 'https://qiwi.com/payment/form/99?amountFraction=0.0&currency=RUB&extra%5B%27account%27%5D=79258550898&extra%5B%27comment%27%5D=' + user_id + '&amountInteger=' + price
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='Перейти к оплате', callback_data='payment_success',
                                                         url=qiwi_pay_url)
            keyboard.add(callback_button)
            callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
            keyboard.add(callback_button)
            bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)
        elif sub_months == 'un':
            price = '4500'

            payments[payments_count]['price'] = price
            msg = 'Нажмите на кнопку для оплаты. ' \
                  'Ссылка действительна 30 минут.' \
                  'Не меняйте комментарий при оплате. ' \
                  'После ее совершения вам придет сообщение об открытии полного функционала бота.'

            qiwi_pay_url = 'https://qiwi.com/payment/form/99?amountFraction=0.0&currency=RUB&extra%5B%27account%27%5D=79258550898&extra%5B%27comment%27%5D=' + user_id + '&amountInteger=' + price
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='Перейти к оплате', callback_data='payment_success',
                                                         url=qiwi_pay_url)
            keyboard.add(callback_button)
            callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
            keyboard.add(callback_button)
            bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)
    else:
        msg = 'А можно не оплачивать :) \n' \
              '\n' \
              'Вы и ваш друг получите дополнительно по 1 месяцу расширенного доступа, ' \
              'если ваш друг при регистрации введёт ваш логин и оплатит хотя бы один месяц.'
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text='1 месяц - скидка 0%', callback_data='payment_1_month')
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='3 месяца - скидка 20%', callback_data='payment_3_months')
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='6 месяцев - скидка 30%', callback_data='payment_6_months')
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='12 месяцев - скидка 40%', callback_data='payment_12_months')
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='Безлимит', callback_data='payment_unlimited')
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
        keyboard.add(callback_button)

        bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'refer')
def callback_inline(call):
    refer_count = 0
    promos.append({})
    promos.count = len(promos) - 1
    msg = 'Вы и ваш друг получите дополнительно по 1 месяцу расширенного доступа, если ' \
          'ваш друг при регистрации введёт ваш логин и оплатит хотя бы один месяц. \n' \
          '\n' \
          'Количество приглашенных: ' + str(refer_count)

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
    keyboard.add(callback_button)

    bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'promo')
def callback_inline(call):
    msg = 'Пришлите ваш промокод для активации бонусов:'

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
    keyboard.add(callback_button)

    sent_msg = bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)
    bot.register_next_step_handler(sent_msg, set_promo)


def set_promo(msg):
    promo_succ_msg = 'Промокод успешно активирован'
    promo_unsucc_msg = 'У Вас нет такого промокода'
    bot.send_message(msg.chat.id, promo_succ_msg)


@bot.callback_query_handler(func=lambda call: call.data == 'help')
def callback_inline(call):
    msg = 'Инструкция по ссылке: https://clck.ru/H8HeE \n' \
          '\n' \
          'Открытый чат для общения и решения вопросов: \n' \
          'https://t.me/joinchat/AAGeRBZPliIGwdcIcmqM0Q \n' \
          '\n' \
          'Если будут серьезные вопросы, пишите мне напрямую @alantsoff'

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
    keyboard.add(callback_button)

    bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'stat')
def callback_inline(call):
    msg = 'Перейдите по ссылке для просмотра статистики:'
    sheet_url = ''
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='Смотреть', callback_data='show_stat', url=sheet_url)
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
    keyboard.add(callback_button)

    bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)


def handle_token(message):
    # message_text = int(''.join(message.text.split()))
    print('hello im here')
    new_bot_token = ''.join(message.text).split()[0]
    if len(new_bot_token) == 45:
        try:
            _bot_info = telebot.TeleBot(new_bot_token).get_me()
            bot_info = dict()
            bot_info['owner_id'] = str(message.from_user.id)
            bot_info['bot_id'] = str(_bot_info.id)
            bot_info['bot_username'] = '@' + str(_bot_info.username)
            print(bot_info)
            threads_bot.append({})
            threads_bot_count = len(threads_bot) - 1
            threads_bot[threads_bot_count]['target'] = new_bot
            threads_bot[threads_bot_count]['args'] = [new_bot_token]
            print(threads_bot[threads_bot_count]['args'])
            print(len(threads_bot[threads_bot_count]['args']))
            threads_bot[threads_bot_count]['name'] = str(bot_info['bot_username'])
            threads_bot[threads_bot_count]['daemon'] = True
            new_bot_thread = th.Thread(target=threads_bot[threads_bot_count]['target'], name=threads_bot[threads_bot_count]['name'], args=(threads_bot[threads_bot_count]['args']), daemon=threads_bot[threads_bot_count]['daemon'])
            new_bot_thread.start()
            # new_bot(new_bot_token)
            bot.send_message(message.chat.id, 'Бот ' + bot_info['bot_username'] + ' успешно запущен!', parse_mode='html')
        except:
            bot.send_message(message.chat.id,
                             'Упс... что-то не так с токеном :( \n Перепроверьте его, если эта ошибка возникла снова — вернитесь в @BotFather и перевыпустите токен командой /revoke, а потом отправьте его мне.',
                             parse_mode='html')


    else:
        bot.send_message(message.chat.id, 'Упс... что-то не так с токеном :( \n Перепроверьте его, если эта ошибка возникла снова — вернитесь в @BotFather и перевыпустите токен командой /revoke, а потом отправьте его мне.', parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data == 'set_refer')
def callback_inline(call):
    msg = 'Введите никнейм пользователя, который Вас пригласил, чтобы получить бонус в размере одного ' \
          'бесплатного месяца подписки при оплате хотя бы одного месяца:'

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='Назад', callback_data='cab')
    keyboard.add(callback_button)

    sent_msg = bot.send_message(call.message.chat.id, msg, parse_mode='html', reply_markup=keyboard)
    bot.register_next_step_handler(sent_msg, set_refer)


def set_refer(message):
    msg = 'Вам и Вашему другу успешно начислен бонус!'

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='СОЗДАТЬ БОТА', callback_data='newbot')
    keyboard.add(callback_button)

    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True)

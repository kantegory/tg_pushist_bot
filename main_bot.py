import telebot
from telebot import types

token = 'YOUR-BOT-TOKEN'
bot = telebot.TeleBot(token)
telebot.apihelper.proxy = {'https': 'socks5://userproxy:password@ip:port'}


@bot.message_handler(commands=['start'])
def handle_start(message):
    language = message.from_user.language_code
    user_id = message.from_user.id
    hello_msg = "Я помогаю контролировать сотрудников через чаты. \n" \
                "\n" \
                "Напоминаю нужным людям в нужные дни о том, что им нужно делать. " \
                "Попробуй меня и напиши @alantsoff обо мне отзыв."
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="ПОЕХАЛИ", callback_data="newbot")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, hello_msg, reply_markup=keyboard, parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data == 'newbot')
def callback_inline(call):
    msg = '1. Перейдите в бот @BotFather и создайте новый бот. \n' \
          '2. После создания бота вы получите токен бота (выглядит вот так – ' \
          '<code>123456:ABC-DEF1234gh...</code>) – ' \
          'скопируйте его сюда и отправьте.'

    bot.send_message(call.message.chat.id, msg, parse_mode='html')


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
    if call.data[7:]:
        sub = call.data[8:]
        sub_months = sub[0:2] if "_" not in sub[0:2] else sub[0:1]
        print(sub_months)
        if sub_months == '1':
            price = '249'
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


@bot.message_handler(content_types=['text'])
def handle_text(message):
    # message_text = int(''.join(message.text.split()))
    print('hello im here')
    message_text = ''.join(message.text).split()[0]
    if len(message_text) == 45:
        new_bot_token = message_text
        new_bot(new_bot_token)
        bot.send_message(message.chat.id, 'Спасибо за токен', parse_mode='html')


def new_bot(usr_token):
    new_bot = telebot.TeleBot(usr_token)

    @new_bot.message_handler(commands=['start'])
    def handle_start(message):
        language = message.from_user.language_code
        hello_msg = "Я помогаю контролировать сотрудников через чаты. \n" \
                    "\n" \
                    "Напоминаю нужным людям в нужные дни о том, что им нужно делать. " \
                    "Попробуй меня и напиши @alantsoff обо мне отзыв."
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="ПОЕХАЛИ", callback_data="newbot")
        keyboard.add(callback_button)
        new_bot.send_message(message.chat.id, hello_msg, reply_markup=keyboard, parse_mode='html')

    new_bot.polling(none_stop=True)


if __name__ == '__main__':
    bot.polling(none_stop=True)

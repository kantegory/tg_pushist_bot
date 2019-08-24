from db import Users, Bots, Requests, Chats, Payments, Promos, session
from sqlalchemy import select, delete
s = session()


def user_add(user):
    rows = s.query(Users).all()
    check = []
    for row in rows:
        check.append(row.user_tg_id)
    for curr_row in user:
        if str(curr_row['user_tg_id']) not in check:
            users = Users(
                user_tg_id=curr_row['user_tg_id'],
                user_language=curr_row['user_language'],
                user_name=curr_row['user_name'],
                user_refer_name=curr_row['user_refer_name'],
                user_status=curr_row['user_status'],
                user_registration_date=curr_row['user_registration_date']
            )
            s.add(users)
    s.commit()


def bot_add(bot):
    print(bot)
    rows = s.query(Bots).all()
    check = []
    for row in rows:
        check.append(row.bot_tg_id)

    for curr_row in bot:
        if curr_row['bot_tg_id'] not in check:
            bots = Bots(
                bot_name=curr_row['bot_username'],
                bot_tg_id=curr_row['bot_tg_id'],
                user_id=curr_row['user_id'],
                bot_stat=curr_row['bot_stat']
            )
            s.add(bots)
            print(bots)
        s.commit()


def request_add(request):
    
    for curr_row in request:
    
        requests = Requests(
            request_text=str(curr_row['request_text']),
            request_period=str(curr_row['request_period']),
            request_period_opts=str(curr_row['request_period_opts']),
            request_start_date=curr_row['request_start_date'],
            request_time=curr_row['request_time'],
            request_end_date=curr_row['request_end_date'],
            user_id=curr_row['user_id'],
            chat_id=curr_row['chat_id'],
            request_create_date=curr_row['request_create_date']
        )
        s.add(requests)

    s.commit()

    
def chat_add(chat):
    
    rows = s.query(Chats).all()
    check = []
    for row in rows:
        check.append(row.chat_tg_id)

    for curr_row in chat:
        if curr_row['chat_tg_id'] not in check:
            chats = Chats(
                chat_tg_id=curr_row['chat_tg_id'],
                chat_title=curr_row['chat_title'],
                bot_id=curr_row['bot_id']
            )
            s.add(chats)

    s.commit()


def payment_add(payment):
    
    for curr_row in payment:
        payments = Payments(
            payment_amount=curr_row['payment_amount'],
            user_id=curr_row['user_id'],
            payment_end_date=curr_row['payment_end_date'],
            promo_value=curr_row['promo_value']
        )
        s.add(payments)

    s.commit()


def promo_add(promo):

    rows = s.query(Promos).all()
    check = []
    for row in rows:
        check.append(row.promo_value)

    for curr_row in promo:
        if curr_row['promo_value'] not in check:
            promos = Promos(
                promo_value=curr_row['promo_value'],
                promo_start_date=curr_row['promo_start_date'],
                promo_action=curr_row['promo_action'],
                promo_end_date=curr_row['promo_end_date']
            )
            s.add(promos)

    s.commit()


def select_user(user_tg_id):
    rows = s.query(Users).filter(Users.user_tg_id == str(user_tg_id)).all()
    result = [{'user_id': rows[i].user_id, 'user_name': rows[i].user_name, 'user_language': rows[i].user_language,
               'user_refer_name': rows[i].user_refer_name, 'user_tg_id': rows[i].user_tg_id,
               'user_status': rows[i].user_status, 'user_registration_date': rows[i].user_registration_date}
              for i in range(len(rows))]
    return result


def select_user_by_name(user_name):
    rows = s.query(Users).filter(Users.user_name == user_name).all()
    result = [{'user_id': rows[i].user_id, 'user_name': rows[i].user_name, 'user_language': rows[i].user_language,
               'user_refer_name': rows[i].user_refer_name, 'user_tg_id': rows[i].user_tg_id,
               'user_status': rows[i].user_status, 'user_registration_date': rows[i].user_registration_date}
              for i in range(len(rows))]
    return result


def select_user_by_refer_name(refer_name):
    rows = s.query(Users).filter(Users.user_refer_name == refer_name).all()
    result = [{'user_id': rows[i].user_id, 'user_name': rows[i].user_name, 'user_language': rows[i].user_language,
               'user_refer_name': rows[i].user_refer_name, 'user_tg_id': rows[i].user_tg_id,
               'user_status': rows[i].user_status, 'user_registration_date': rows[i].user_registration_date}
              for i in range(len(rows))]
    return result


def select_users():
    rows = s.query(Users).all()
    result = [{'user_id': rows[i].user_id, 'user_name': rows[i].user_name, 'user_language': rows[i].user_language,
               'user_refer_name': rows[i].user_refer_name, 'user_tg_id': rows[i].user_tg_id,
               'user_status': rows[i].user_status, 'user_registration_date': rows[i].user_registration_date}
              for i in range(len(rows))]
    return result


def select_bot(bot_tg_id):
    rows = s.query(Bots).filter(Bots.bot_tg_id == bot_tg_id).all()
    result = [{'bot_id': rows[i].bot_id, 'bot_name': rows[i].bot_name,
               'user_id': rows[i].user_id, 'bot_stat': rows[i].bot_stat} for i in range(len(rows))]
    return result


def select_bot_by_user_id(user_id):
    rows = s.query(Bots).filter(Bots.user_id == user_id).all()
    result = [{'bot_name': rows[i].bot_name, 'bot_stat': rows[i].bot_stat} for i in range(len(rows))]
    return result


def select_request(user_id, chat_id):
    rows = s.query(Requests).filter(Requests.user_id == user_id, Requests.chat_id == chat_id).all()
    result = [{'request_id': rows[i].request_id, 'request_text': rows[i].request_text,
               'request_period': rows[i].request_period, 'request_period_opts': rows[i].request_period_opts,
               'request_start_date': rows[i].request_start_date, 'request_end_date': rows[i].request_end_date,
               'request_chat_id': rows[i].chat_id, 'request_time': rows[i].request_time,
               'request_create_date': rows[i].request_create_date}
              for i in range(len(rows))]
    return result


def select_request_by_user_id(user_id):
    rows = s.query(Requests).filter(Requests.user_id == user_id).all()
    result = [{'request_id': rows[i].request_id, 'request_text': rows[i].request_text,
               'request_period': rows[i].request_period, 'request_period_opts': rows[i].request_period_opts,
               'request_start_date': rows[i].request_start_date, 'request_end_date': rows[i].request_end_date,
               'request_chat_id': rows[i].chat_id, 'request_time': rows[i].request_time,
               'request_create_date': rows[i].request_create_date}
              for i in range(len(rows))]
    return result


def select_requests():
    rows = s.query(Requests).all()
    result = [{'request_id': rows[i].request_id, 'request_text': rows[i].request_text,
               'request_period': rows[i].request_period, 'request_period_opts': rows[i].request_period_opts,
               'request_start_date': rows[i].request_start_date, 'request_end_date': rows[i].request_end_date,
               'request_chat_id': rows[i].chat_id, 'request_time': rows[i].request_time,
               'request_create_date': rows[i].request_create_date}
              for i in range(len(rows))]
    return result


def select_chat(bot_id):
    rows = s.query(Chats).filter(Chats.bot_id == bot_id).all()
    result = [{'chat_tg_id': rows[i].chat_tg_id, 'chat_id': rows[i].chat_id, 'chat_title': rows[i].chat_title}
              for i in range(len(rows))]
    return result


def select_payment(user_id):

    rows = s.query(Payments).filter(Payments.user_id == str(user_id)).all()

    result = [
        {
            'payment_amount': rows[i].payment_amount,
            'payment_end_date': rows[i].payment_end_date,
            'promo_value': rows[i].promo_value,
            'payment_id': rows[i].payment_id,
            'user_id': rows[i].user_id
        }
        for i in range(len(rows))
    ]

    return result


def select_promos(user_id):

    rows = s.query(Payments).filter(Payments.user_id == user_id, Payments.payment_amount == '').all()

    result = [
        {
            'payment_amount': rows[i].payment_amount,
            'payment_end_date': rows[i].payment_end_date,
            'promo_value': rows[i].promo_value,
            'payment_id': rows[i].payment_id,
            'user_id': rows[i].user_id
        }
        for i in range(len(rows))
    ]

    return result


def select_payments():

    rows = s.query(Payments).filter(Payments.promo_value == '').all()

    result = [
        {
            'payment_amount': rows[i].payment_amount,
            'payment_end_date': rows[i].payment_end_date,
            'promo_value': rows[i].promo_value,
            'payment_id': rows[i].payment_id,
            'user_id': rows[i].user_id
        }
        for i in range(len(rows))
    ]

    return result


def select_promos_count():

    rows = s.query(Payments).filter(Payments.promo_value is not '', Payments.payment_amount == '').all()

    result = [
        {
            'payment_amount': rows[i].payment_amount,
            'payment_end_date': rows[i].payment_end_date,
            'promo_value': rows[i].promo_value,
            'payment_id': rows[i].payment_id,
            'user_id': rows[i].user_id
        }
        for i in range(len(rows))
    ]

    return result


def select_promo():
    rows = s.query(Promos).all()
    result = [
        {
            'promo_id': rows[i].promo_id,
            'promo_value': rows[i].promo_value,
            'promo_start_date': rows[i].promo_start_date,
            'promo_action': rows[i].promo_action,
            'promo_end_date': rows[i].promo_end_date
        }
        for i in range(len(rows))
    ]
    return result


def select_promo_by_id(promo_id):
    rows = s.query(Promos).filter(Promos.promo_id == promo_id).all()
    result = [
        {
            'promo_id': rows[i].promo_id,
            'promo_value': rows[i].promo_value,
            'promo_start_date': rows[i].promo_start_date,
            'promo_action': rows[i].promo_action,
            'promo_end_date': rows[i].promo_end_date
        }
        for i in range(len(rows))
    ]
    return result


def delete_request(request_id):
    s.query(Requests).filter(Requests.request_id == int(request_id)).delete()
    s.commit()


def delete_promo(promo_id):
    s.query(Promos).filter(Promos.promo_id == int(promo_id)).delete()
    s.commit()


def update_user_status(user_tg_id, new_status):
    s.query(Users).filter(Users.user_tg_id == str(user_tg_id)).update({'user_status': new_status})
    s.commit()


def update_bot_stat(bot_tg_id, new_bot_stat):

    s.query(Bots).filter(Bots.bot_tg_id == str(bot_tg_id)).update({'bot_stat': new_bot_stat})
    s.commit()

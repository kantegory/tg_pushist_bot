from sqlalchemy import Column, String, Integer, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///pushist.db?check_same_thread=False")
session = sessionmaker(bind=engine)


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    user_tg_id = Column(String)
    user_name = Column(String)
    user_language = Column(String)
    user_refer_name = Column(String)
    user_status = Column(String)
    user_registration_date = Column(String)


class Bots(Base):
    __tablename__ = "bots"
    bot_id = Column(Integer, primary_key=True)
    bot_tg_id = Column(String)
    bot_name = Column(String)
    user_id = Column(Integer)  # owner_id
    bot_stat = Column(String)


class Requests(Base):
    __tablename__ = "requests"
    request_id = Column(Integer, primary_key=True)
    request_text = Column(String)
    request_period = Column(String)
    request_period_opts = Column(String)
    request_start_date = Column(String)
    request_time = Column(String)
    request_end_date = Column(String)
    request_create_date = Column(String)
    user_id = Column(Integer)
    chat_id = Column(Integer)


class Chats(Base):
    __tablename__ = "chats"
    chat_id = Column(Integer, primary_key=True)
    chat_tg_id = Column(String)
    chat_title = Column(String)
    bot_id = Column(String)


class Payments(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True)
    payment_amount = Column(Integer)
    payment_end_date = Column(String)
    user_id = Column(Integer)
    promo_value = Column(String)


class Promos(Base):
    __tablename__ = "promos"
    promo_id = Column(Integer, primary_key=True)
    promo_value = Column(String)
    promo_start_date = Column(String)
    promo_end_date = Column(String)
    promo_action = Column(String)


Base.metadata.create_all(bind=engine)

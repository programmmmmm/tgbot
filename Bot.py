import io
import os
import uuid
import time
import json
import openai
import random
import string
import hashlib
import logging
import tiktoken

from datetime import datetime, timedelta

import requests
import threading
import traceback
from flask import Flask, request
from yookassa import Configuration, Payment

from firebase_admin import credentials, initialize_app, db

import telegram
from telegram import Bot
from telegram.utils.helpers import mention_html
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram import Voice, Audio


#import soundfile as sf
#from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
#import torch

#logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


# Токены
#TELEGRAM_BOT_TOKEN = "578131:AAFFcu7ekjO8i65j0"  # Тестовый
TELEGRAM_BOT_TOKEN = "62485953:AAFR9gekEA8Nr9Ao" #Рабочий
bot2 = Bot(token=TELEGRAM_BOT_TOKEN)
cred = credentials.Certificate("telegabot-16d96-firvsi1b-ae3594244d.json")
initialize_app(cred, {'databaseURL': 'https://telegabot-16d96-defrope-west1.firebasedatabase.app/'})


#Openai токены
OPENAI_API_KEY = "sk-I2DnbmALAFBqqlQ5MzlDshc8cB"
openai.api_key = OPENAI_API_KEY


#ЮKassa токены
SECRET_KEY = "live_MRRA6IBEnh0PA160XnqS6tq8mKkvh8IG2OQ8fNPhZ-Q"
Configuration.account_id = "312066"
Configuration.secret_key = SECRET_KEY


#Распознавание речи токены
#model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-russian")
#tokenizer = Wav2Vec2Tokenizer.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-russian")


typing_messages = [
    "ChatGPT активирует сверхсекретные знания... 🤖",
    "Подключаюсь к великому искусственному интеллекту... 💡",
    "Ищу ответ в глубинах интернета... 🌐",
    "Взламываю библиотеку Александрии... 📚",
    "Сканирую все книги мира... 📖",
    "Собираю информацию со всей Галактики... 🌌",
    "Шифрую ответ, чтобы его не украли... 🔒",
    "Ваш вопрос стоит миллион... 💰",
    "Анализирую все возможные варианты ответов... 🧠",
    "Собираю команду экспертов для вашего вопроса... 👩‍🔬👨‍🔬",
    "Загружаю кристаллический шар для предсказаний... 🔮",
    "Ищу мудрость в пустыне Гоби... 🏜️",
    "Консультируюсь с волшебными существами... 🧚",
    "Задаю вопрос самому себе в прошлом... 🕰️",
    "Читаю мысли знаменитых ученых... 🧪",
    "Прокачиваю мозг до максимального уровня... 🎮",
    "Перегружаюсь на максимальную мощность... 🚀",
    "Восстанавливаю доступ к потерянным знаниям Атлантиды... 🌊",
    "Обучаюсь телепатии для получения ответа... ⚛️",
    "Проверяю весь интернет за секунду... ⏱️",
    "Собираю кубик Рубика для размышления... 🧩",
    "Советуюсь с мудрыми совами Гогвартса... 🦉",
    "Загадываю вопрос на кофейной гуще... ☕",
    "Обращаюсь к Джинну из волшебной лампы... 🧞",
    "Использую временную машину для поиска ответа... ⏳",
    "Активирую режим максимальной концентрации... 👁️",
    "Консультируюсь с космическими черепашками-ниндзя... 🐢",
    "Проверяю знания с бесконечным источником информации... 🧙",
    "Пересматриваю все эпизоды 'Рика и Морти' за ответами... 📺",
    "Использую детектор лжи для фильтрации неправильных ответов... 🕵️",
    "Приглашаю крутого детектива для разгадки вашего вопроса... 🎩",
    "Задаю вопрос всемирной паутине мудрецов... 🕸️",
    "Использую древнее искусство истины для поиска ответа... 🀄",
    "Запрашиваю мудрость с вершины горы... 🏔️",
    "Консультируюсь с дельфинами-гениями... 🐬",
    "Провожу эксперимент в параллельном мире... 🌍",
    "Совершаю временное путешествие для поиска ответа... 🕗",
    "Прошу мудрого старца из деревни знаний... 🧓",
    "Использую магический компас для навигации к ответу... 🧭",
    "Загадываю вопрос древнему дракону... 🐉",
    "Собираю информацию с тысячи планет... 🪐",
    "Просматриваю все знания Хогвартса... 🏰",
    "Консультируюсь с оракулом Дельфи... 🏺",
    "Использую методы Шерлока Холмса для поиска ответа... 🔍",
    "Приглашаю команду супергероев для совета... 🦸",
    "Слушаю шепот деревьев мудрости... 🌳",
    "Взламываю матрицу для поиска правды... 💻",
    "Активирую глобальный поиск знаний... 🌎",
    "Загадываю вопрос Хаттори Ханзо из 'Килл Билл'... ⚔️",
    "Обращаюсь к Тони Старку за научными советами... 🦾",
    "Получаю помощь от героев 'Мстителей'... 🦸",
    "Провожу анализ ситуации вместе с 'Терминатором'... 🤖",
    "Спрашиваю мастеров дзен из 'Кунг-фу панды'... 🐼",
    "Собираю знания с 'Трансформерами'... 🚛",
    "Советуюсь с героями 'Шестого чувства'... 👻",
    "Загадываю вопрос Брюсу Уэйну из 'Бэтмена'... 🦇",
    "Обращаюсь к Шерлоку Холмсу за советом... 🔎",
    "Консультируюсь с героями 'Пиратов Карибского моря'... ☠️",
    "Обращаюсь к мастеру Йоде из 'Звездных войн'... 🟢",
    "Спрашиваю героев 'Оушена' за идеи... 💎",
    "Загадываю вопрос Леону из 'Леон: Заводной профессионал'... 🌿",
    "Ищу знания у героев 'Матрицы'... 🕴️",
    "Обращаюсь к 'Звездному лорду' за помощью... 🚀",
    "Советуюсь с 'Эллиотом' из 'Инопланетянина'... 🚲",
    "Загадываю вопрос агентам 'Мен in Black'... 🕶️",
]


# Создайте списки с предложениями для каждого случая
week_messages = [
    "Оплата прошла успешно! Наслаждайтесь недельным доступом к боту 🌈",
    "Успешно оплачено! Ваша неделя с ботом начинается прямо сейчас 🎯",
    "Платеж получен! Целая неделя использования бота впереди 🏁",
    "Оплата подтверждена! Неделя без ограничений с ботом началась 🎊",
    "Успешная оплата! Неделя незабываемого использования бота ждет вас 🌟",
    "Платеж успешно завершен! Наслаждайтесь использованием бота на протяжении следующей недели 🎉",
    "Успешный платеж! Вы можете пользоваться ботом в течение одной недели 🥳",
    "Платеж прошел успешно! Неделя безграничного использования бота начинается сейчас 🚀",
]

month_messages = [
    "Оплата прошла успешно! Вас ждет месяц полного доступа к боту 🌠",
    "Успешно оплачено! Готовьтесь к месяцу использования бота без границ 🎯",
    "Платеж получен! Впереди месяц активного использования бота 🏁",
    "Оплата подтверждена! Месяц непрерывного использования бота начался 🎊",
    "Успешная оплата! Месяц волшебного использования бота уже здесь 🌟",
    "Платеж успешно завершен! Весь месяц безграничного использования бота в вашем распоряжении 🎊",
    "Успешный платеж! Наслаждайтесь месяцем использования бота 🌟",
    "Платеж прошел успешно! Вам доступен месяц безграничного использования бота 🎈",
]

year_messages = [
    "Оплата прошла успешно! Вас ждет год полного доступа к боту 🌈",
    "Успешно оплачено! Готовьтесь к году использования бота без ограничений 🎯",
    "Платеж получен! Впереди год активного использования бота 🏁",
    "Оплата подтверждена! Год непрерывного использования бота начался 🎊",
    "Успешная оплата! Год волшебного использования бота уже здесь 🌟",
    "Платеж успешно завершен! Год безграничного использования бота ждет вас 🥇",
    "Успешный платеж! Впереди целый год использования бота без ограничений 🏆",
    "Платеж прошел успешно! Наслаждайтесь годом безграничного использования бота 🎉",
]


# Задаем уровень логов
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
updater = Updater(token=TELEGRAM_BOT_TOKEN)
dispatcher = updater.dispatcher

# Клавиатура с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Задать вопрос 🔍"),
            KeyboardButton(text="Возможности 🤖"),
        ],
        [
            KeyboardButton(text="Мой баланс GP 💰"),
            KeyboardButton(text="Заработать GP 🆓"),
        ],
        [
            KeyboardButton(text="Купить GP 💳"),
            KeyboardButton(text="Очистить диалог с ботом 🧼"),
        ]
    ],
    resize_keyboard=True
)


#Кнопки подписки
subscription_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Подписаться 🖊️", url="https://t.me/NeuroNewsGpt")],
        [InlineKeyboardButton("Проверить подписку ✅", callback_data="check_subscription")]
    ]
)


#------------------------------ВСЁ ЧТО СВЯЗАНО С БАЗОЙ ДАННЫХ------------------------------


def generate_unique_code(user_id):
    return f"{user_id}-{str(uuid.uuid4())[:8]}"


def generate_invite_link(bot_username, unique_code):
    return f"https://t.me/{bot_username}?start={unique_code}"


def add_new_user(user_id):
    unique_code = generate_unique_code(user_id)
    invite_link = generate_invite_link("ChatProGPT_bot", unique_code)
    ref = db.reference(f'users/{user_id}')
    ref.set({
        'gp': 15,
        'subscription': "none",
        'referral_code': invite_link,
        'referal_bro': "none"
    })


def save_subs_date(user_id, code):
    if isinstance(code, datetime):
        code = code.isoformat()
    ref = db.reference(f'users/{user_id}/subscription')
    ref.set(code)


def get_subs_date(user_id):
    ref = db.reference(f'users/{user_id}/subscription')
    code = ref.get()

    if code is None or code == "none":
        return "none"
    else:
        return datetime.fromisoformat(code)


def save_referral_code(user_id, code):
    ref = db.reference(f'users/{user_id}/referral_code')
    ref.set(code)


def get_referral_code(user_id):
    ref = db.reference(f'users/{user_id}/referral_code')
    return ref.get()


def referral_code(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    referral_code = get_referral_code(user_id)
    if referral_code:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"<b>💎 Зарабатывайте GP - просто и без лишних затрат!</b>\n\n1. Приглашайте друзей в нашего бота и получайте +7GP за каждого нового участника (важно, приглашайте друзей только по реферальной ссылке)👥\n\nВот ваша персональная реферальная ссылка: {referral_code}\n\n🌱 В скором времени появятся новые способы получения GP бесплатно. Оставайтесь с нами и будьте в курсе обновлений!\n\n",
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True)

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="К сожалению, возникла проблема с получением реферальной ссылки 😔 Повторите попытку позже ⏳"
        )


def find_inviter_id(unique_code):
    users_ref = db.reference('users')
    users_data = users_ref.get()

    for user_id, user_data in users_data.items():
        referral_link = user_data.get('referral_code')
        if referral_link and unique_code in referral_link:
            return user_id
    return None


def save_inviter_id(user_id, inviter_id):
    ref = db.reference(f'users/{user_id}/inviter_id')
    ref.set(inviter_id)


def get_inviter_id(user_id):
    ref = db.reference(f'users/{user_id}/inviter_id')
    return ref.get()


def delete_inviter_id(user_id):
    ref = db.reference(f'users/{user_id}/inviter_id')
    ref.delete()


def ensure_user_in_db(handler_function):
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if not user_exists(user_id):
            add_new_user(user_id)
        return handler_function(update, context, *args, **kwargs)
    return wrapper


def user_exists(user_id):
    ref = db.reference(f'users/{user_id}')
    return ref.get() is not None


def get_user_data(user_id, field):
    ref = db.reference(f'users/{user_id}/{field}')
    return ref.get()


def set_user_data(user_id, field, value):
    ref = db.reference(f'users/{user_id}/{field}')
    ref.set(value)


def update_user_data(user_id, chat_data, updated_data):
    chat_data[user_id].update(updated_data)


@ensure_user_in_db
def my_data(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    current_subs = get_user_data(user_id, 'subscription')
    current_gp = get_user_data(user_id, 'gp')
    update.message.reply_text(f"<b>💰 Узнайте свой баланс и статус подписки!</b>\n\nТекущий баланс:\n{current_gp}GP 💎\n\nПодписка:\n{current_subs} ⏱️", parse_mode=telegram.ParseMode.HTML)
    #context.bot.send_message(f"Ваш тарифный план: {current_gp}GP")


#------------------------------START------------------------------


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if not user_exists(user_id):
        add_new_user(user_id)
        if context.args and len(context.args) == 1:
            print("hello")
            inviter_unique_code = context.args[0]
            inviter_id = find_inviter_id(inviter_unique_code)
            if inviter_id:
                save_inviter_id(user_id, inviter_id)
        if check_subscription(update, context):
            inviter_id = get_inviter_id(user_id)
            if inviter_id:
                # Начисление 1 GP пользователю, который пригласил друга
                current_gp = get_user_data(inviter_id, 'gp')
                set_user_data(inviter_id, 'gp', current_gp + 7)
                # Отправка сообщения пользователю, который пригласил друга
                friend_link = mention_html(user_id, "друг")
                context.bot.send_message(
                    chat_id=inviter_id,
                    text=f"Ура! Ваш {friend_link} присоединился к 'ChatGPT | FREE' и вам начислено +7GP! 🥳",
                    parse_mode=telegram.ParseMode.HTML
                )
                # Удаление inviter_id из базы данных, чтобы не начислять GP повторно
                delete_inviter_id(user_id)

    context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Здравствуйте, {user_name}! \n\n🌞 Я ChatGPT, ваш личный помощник и искусственный интеллект 🧠", reply_markup=keyboard)


def handle_features(update: Update, context: CallbackContext):
    message = context.bot.send_message(chat_id=update.effective_chat.id, text=
"<b>🎓 Откройте магический мир учёбы с помощью ChatGPT:</b>\n\n"
"1️⃣ Разгадайте тайны математики и физики! 🔢🔬\n\n"
"2️⃣ Освойте историю, литературу и географию в одно мгновение! 📚🌏\n\n"
"3️⃣ Станьте звездой химии и биологии без усилий! ⚗️🌱\n\n"
"4️⃣ Изучайте иностранные языки как никогда прежде! 🌍💬\n\n"
"5️⃣ Проходите сквозь стены кода и программирования! 💻🚀\n\n"
"6️⃣ Откройте секреты успеха в личной и профессиональной жизни! 🎯🌟\n\n"
"💎 Это лишь малая часть моих возможностей! Раскройте всю мощь ChatGPT и обращайтесь со своими задачами – я готов помочь! 😉\n\n"
"Тыкните на кнопку ниже и погрузитесь в мир невероятных знаний и возможностей! 👇",
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton("Задать вопрос 🔍", callback_data="ask_question")]]),
                             parse_mode=telegram.ParseMode.HTML)
    context.user_data["features_message_id"] = message.message_id


#------------------------------ПРОВЕРКА ПОДПИСКИ------------------------------


def handle_after_subscription(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    query = update.callback_query

    if check_subscription(update, context):
        query.edit_message_text(text="<b>Благодарю вас за подписку! 🤗</b>\n\nТеперь можете задать свой вопрос:", parse_mode=telegram.ParseMode.HTML)

        inviter_id = get_inviter_id(user_id)
        if inviter_id:
            # Начисление 1 GP пользователю, который пригласил друга
            current_gp = get_user_data(inviter_id, 'gp')
            set_user_data(inviter_id, 'gp', current_gp + 7)
            # Отправка сообщения пользователю, который пригласил друга
            friend_link = mention_html(user_id, "друг")
            context.bot.send_message(
                chat_id=inviter_id,
                text=f"Ура! Ваш {friend_link} присоединился к 'ChatGPT | FREE' и вам начислено +7GP! 🥳",
                parse_mode=telegram.ParseMode.HTML
            )
            # Удаление inviter_id из базы данных, чтобы не начислять GP повторно
            delete_inviter_id(user_id)

        handle_ask_question(update, context)

    else:
        query.answer("Подпишитесь на канал 📰")


def is_user_subscribed(bot, user_id, channel_username):
    try:
        chat_member = bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        return chat_member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False


def check_subscription(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    channel_username = '@NeuroNewsGpt'

    if is_user_subscribed(context.bot, user_id, channel_username):
        return True
    else:
        return False


#------------------------------Задать вопрос------------------------------


#def speech_to_text(audio_file):
#    speech, _ = sf.read(audio_file)
#    input_values = tokenizer(speech, return_tensors="pt").input_values
#    logits = model(input_values).logits
#    predicted_ids = torch.argmax(logits, dim=-1)
#    text = tokenizer.batch_decode(predicted_ids)[0]
#    return text
#
#
## Обработчик голосовых сообщений
#def handle_voice_message(update, context):
#    voice_message = update.message.voice
#    file = context.bot.get_file(voice_message.file_id)
#    audio_bytes = io.BytesIO(requests.get(file.file_path).content)
#    audio_file = "audio.wav"
#    with open(audio_file, "wb") as f:
#        f.write(audio_bytes.read())
#    text = speech_to_text(audio_file)
#    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
#
#
## Обработчик аудиосообщений
#def handle_audio_message(update, context):
#    audio_message = update.message.audio
#    file = context.bot.get_file(audio_message.file_id)
#    audio_bytes = io.BytesIO(requests.get(file.file_path).content)
#    audio_file = "audio.wav"
#    with open(audio_file, "wb") as f:
#        f.write(audio_bytes.read())
#    text = speech_to_text(audio_file)
#    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
#

def save_message(context: CallbackContext, user_id: int, role: str, content: str):
    if "messages" not in context.user_data:
        context.user_data["messages"] = []

    context.user_data["messages"].append({"role": role, "content": content})


def clear_messages(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.user_data["messages"] = []
    context.bot.send_message(chat_id=chat_id, text="Диалог с ботом успешно очищен! 🗑️")


# Обработка нажатия на кнопку "Задать вопрос"
@ensure_user_in_db
def handle_ask_question(update: Update, context: CallbackContext):

    if context.user_data.get("waiting_for_answer"):
        return

    if not check_subscription(update, context):
        try:
            query = update.callback_query
            query.answer()
            chat_id = query.message.chat_id
            message_id = context.user_data["features_message_id"]
            context.bot.edit_message_text(chat_id=chat_id,message_id = message_id,
                                     text="<b>🤖 Для доступа к функциям бота:</b>\n\n1.Подпишитесь на канал:\n@NeuroNewsGpt 📰\n\n2.Нажмите на кнопку:\n'Проверить подписку ✅'",
                                     reply_markup=subscription_keyboard, parse_mode=telegram.ParseMode.HTML)
            return
        except Exception:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="<b>🤖 Для доступа к функциям бота:</b>\n\n1.Подпишитесь на канал:\n@NeuroNewsGpt 📰\n\n2.Нажмите на кнопку:\n'Проверить подписку ✅'",
                                     reply_markup=subscription_keyboard, parse_mode=telegram.ParseMode.HTML)
            return

    elif update.callback_query:
        query = update.callback_query
        query.answer()
        chat_id = query.message.chat_id
        message_id = context.user_data["features_message_id"]
        context.user_data["asking_question"] = True
        context.bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text="Введите ваш вопрос:")


    elif update.message:
        user_id = update.effective_user.id

        if get_subs_date(user_id) != "none":
            try:
                now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                dt_str = get_subs_date(user_id).strftime("%Y-%m-%d %H:%M:%S")
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                if dt <= now:
                    save_subs_date(user_id, "none")
            except ValueError:
                pass

        user_id = update.message.from_user.id
        user_data = get_user_data(user_id, 'gp')
        user_data_subs = get_user_data(user_id, 'subscription')
        if user_data_subs == "none":
            if user_data <= 0:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Ой, у вас не хватает GP или ваша подписка истекла! 🚫\n\nЗаработайте или купите больше GP, или продлите подписку, чтобы задать вопрос 🌟")
                return
        context.user_data["asking_question"] = True
        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите ваш вопрос:")


# Обработка введенного вопроса
@ensure_user_in_db
def handle_question(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    message_text = update.message.text

    if not context.user_data.get("asking_question"):
        handle_text_message(update, context)
        return

    context.user_data["asking_question"] = False
    threading.Thread(target=process_question,
                     args=(update, context, message_text)).start()


#------------------------------Генерация ответа------------------------------


@ensure_user_in_db
def send_typing(update: Update, context: CallbackContext, stop_event):
    chat_id = update.effective_chat.id
    current_typing_messages = typing_messages.copy()
    message = random.choice(current_typing_messages)
    current_typing_messages.remove(message)
    sent_message = context.bot.send_message(chat_id=chat_id, text=message)

    while not stop_event.is_set():
        time.sleep(2)
        if not current_typing_messages:
            current_typing_messages = typing_messages.copy()
            current_typing_messages.remove(message)
        message = random.choice(current_typing_messages)
        current_typing_messages.remove(message)
        context.bot.edit_message_text(chat_id=chat_id, message_id=sent_message.message_id, text=message)

    context.bot.delete_message(chat_id=chat_id, message_id=sent_message.message_id)


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens


@ensure_user_in_db
def process_question(update: Update, context: CallbackContext, promt):
    context.user_data["waiting_for_answer"] = True
    MAX_TOTAL_TOKENS = 4096  # Максимальное количество токенов, которое модель может обработать
    stop_event = threading.Event()
    typing_thread = threading.Thread(target=send_typing, args=(update, context, stop_event))
    typing_thread.start()
    user_id = update.effective_user.id

    RETRY_ATTEMPTS = 5  # Количество повторных попыток
    RETRY_DELAY = 10  # Задержка между попытками (в секундах)

    answer = ""

    # Сохраняем вопрос пользователя
    if context.user_data.get("messages", []) == []:
        save_message(context, user_id, "system", "")
    messages = context.user_data.get("messages")
    print(len(messages))
    if len(messages) == 5:
        messages.pop(0)
    retry_count = 0
    while True:
        try:
            input_tokens = sum(num_tokens_from_string(str(prompt)) for prompt in messages + [{"role": "user", "content": promt}])
            max_tokens = MAX_TOTAL_TOKENS - input_tokens - 1  # Вычитаем 1, чтобы оставить место для токена-разделителя
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages + [{"role": "user", "content": promt}],
                max_tokens=max_tokens,
                n=1,
                temperature=0,
            )

            answer = response['choices'][0]['message']['content']
            print(response['usage']['total_tokens'])
            break

        except openai.error.InvalidRequestError as e:
            if "context length" in str(e):
                messages.pop(0)
            elif "less than the minimum of" in str(e):
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Упс! Ваш запрос слишком большой, не могу справиться 😅")
            else:
                manager = update.effective_message.bot
                error_message = f"Ошибка: {str(e)}\n\n{traceback.format_exc()}"
                manager.send_message(chat_id=5718940340, text=error_message)
                stop_event.set()
                typing_thread.join()
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Ой! Произошла ошибка на моей стороне 🤖\n\nПопробуйте задать вопрос снова позже 🔄")
        except openai.error.RateLimitError:
            if retry_count < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)
                retry_count += 1
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Ой! Кажется, сервера OpenAI в данный момент перегружены, и я не могу предоставить ответ. 🤔\n\nТакие ситуации случаются редко, но, тем не менее, прошу вас повторить запрос через некоторое время. Благодарю за понимание 🙏🕒")
                break

    stop_event.set()
    typing_thread.join()

    max_message_length = 4096

    if answer != "":  # добавьте эту проверку перед отправкой ответа
        max_message_length = 4096

        if len(answer) <= max_message_length:
            context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
        else:
            with io.StringIO(answer) as file:
                file.name = "answer.txt"
                context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename="answer.txt",
                                          caption="Ответ слишком объемный, отправляю его как файл 📤")

        # Сохраняем ответ модели
        save_message(context, user_id, "system", answer)
        current_gp = get_user_data(user_id, 'gp')
        current_subs = get_user_data(user_id, 'subscription')
        if current_subs == "none":
            set_user_data(user_id, 'gp', current_gp - 1)
        else:
            pass
    context.user_data["waiting_for_answer"] = False

#------------------------------Обработка не командных сообщений------------------------------


@ensure_user_in_db
def handle_text_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if check_subscription(update, context):
        if context.user_data.get("asking_question"):
            handle_question(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Чтобы задать вопрос, нажмите на кнопку в меню:\n'Задать вопрос 🔍'",
                                     reply_markup=keyboard)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="<b>🤖 Для доступа к функциям бота:</b>\n\n1.Подпишитесь на канал:\n@NeuroNewsGpt 📰\n\n2.Нажмите на кнопку:\n'Проверить подписку ✅'",
                                 reply_markup=subscription_keyboard, parse_mode=telegram.ParseMode.HTML)


#------------------------------Premium-подписка------------------------------


@ensure_user_in_db
def cancelPay(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Оплата временно приостановлена, но мы работаем над этим! ⚙️")


@ensure_user_in_db
def handle_subscribeGPT(update: Update, context: CallbackContext):
    query = None
    chat_id = update.effective_chat.id
    message_id = None

    if update.callback_query:
        query = update.callback_query
        chat_id = query.message.chat_id
        message_id = query.message.message_id

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("25GP - 19р", callback_data="buy_25"),
         InlineKeyboardButton("50GP - 35р", callback_data="buy_50")],
        [InlineKeyboardButton("200GP - 119р", callback_data="buy_200"),
         InlineKeyboardButton("1 неделя - 199р", callback_data="buy_week")],
        [InlineKeyboardButton("1 месяц - 549р", callback_data="buy_month"),
         InlineKeyboardButton("1 год - 1149р", callback_data="buy_year")],
    ])

    if message_id:
        context.bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text="<b>🌟 Исследуйте доступные варианты покупки GP!</b>\n\nЗдесь вы можете узнать, сколько GP можно получить и какова их стоимость💡",
                                      reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="<b>🌟 Исследуйте доступные варианты покупки GP!</b>\n\nЗдесь вы можете узнать, сколько GP можно получить и какова их стоимость💡",
                                 reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)

    if query:
        query.answer()


def create_payment(amount, description, user_id, return_url, message_id):
    data_to_sign = f"{amount}&{description}&{user_id}&{return_url}&{SECRET_KEY}"
    generated_signature = hashlib.sha256(data_to_sign.encode()).hexdigest()

    metadata = {
        "user_id": user_id,
        "signature": generated_signature,
        "message_id": message_id
    }

    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "capture": True,
        "description": description,
        "metadata": metadata,
        "receipt": {
            "email": "user@example.com",  # Замените на email пользователя, если доступен
            "phone": "79111234567",  # Замените на номер телефона пользователя, если доступен
            "tax_system_code": 1,
            "items": [
                {
                    "description": description,
                    "quantity": "1.00",
                    "amount": {
                        "value": str(amount),
                        "currency": "RUB"
                    },
                    "vat_code": 1,
                    "payment_mode": "full_prepayment",
                    "payment_subject": "commodity"
                }
            ]
        }
    })

    return payment.confirmation.confirmation_url


def handle_buy_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.callback_query.from_user.id
    return_url = "https://t.me/ChatProGPT_bot"

    if query.data == "return_to_choice":
        handle_subscribeGPT(update, context)
        return

    elif query.data == "buy_25":
        confirmation_url = create_payment(19, "25GP - 19р", user_id, return_url, query.message.message_id)
        price_text = "25GP - 19р"
    elif query.data == "buy_50":
        confirmation_url = create_payment(35, "50GP - 35р", user_id, return_url, query.message.message_id)
        price_text = "50GP - 35р"
    elif query.data == "buy_200":
        confirmation_url = create_payment(119, "200GP - 119р", user_id, return_url, query.message.message_id)
        price_text = "200GP - 119р"

    elif query.data == "buy_week":
        confirmation_url = create_payment(199, "1 неделя - 199р", user_id, return_url, query.message.message_id)
        price_text = "1 неделя - 199р"

    elif query.data == "buy_month":
        confirmation_url = create_payment(549, "1 месяц - 549р", user_id, return_url, query.message.message_id)
        price_text = "1 месяц - 549р"
        #context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="Пока что недоступно")

    elif query.data == "buy_year":
        confirmation_url = create_payment(1149, "1 год - 1149р", user_id, return_url, query.message.message_id)
        price_text = "1 год - 1149р"
        #context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="Пока что недоступно")

    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=f"Вы выбрали: {price_text}",
                                  reply_markup=InlineKeyboardMarkup([
                                      [InlineKeyboardButton(f"Оплатить {price_text}", url=confirmation_url)],
                                      [InlineKeyboardButton("Вернуться к выбору ↩️", callback_data="return_to_choice")]]))

    query.answer()


def calculate_gp(description):
    if description == "25GP - 19р":
        return 25
    elif description == "50GP - 35р":
        return 50
    elif description == "200GP - 119р":
        return 200
    if description == "1 неделя - 199р":
        return "week"
    elif description == "1 месяц - 549р":
        return "month"
    elif description == "1 год - 1149р":
        return "year"


def add_gp(user_id, gp_to_add):
    current_gp = get_user_data(user_id, 'gp')
    if current_gp is not None:
        new_gp = current_gp + gp_to_add
        set_user_data(user_id, 'gp', new_gp)


def create_subscription_end_date(user_id, days):
    if get_subs_date(user_id) != "none":
        dt_str = get_subs_date(user_id).strftime("%Y-%m-%d %H:%M:%S")
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        end_date = dt + timedelta(days=days)
    else:
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now + timedelta(days=days)
    return end_date



@app.route('/')
def home():
    return 'Welcome to my application!'


def is_payment_processed(payment_id):
    with open("processed_payments.log", "r") as log_file:
        processed_payments = log_file.readlines()
        if f"{payment_id}\n" in processed_payments:
            return True

    return False


def log_processed_payment(payment_id):
    with open("processed_payments.log", "a") as log_file:
        log_file.write(f"{payment_id}\n")


@app.route('/yookassa_notification', methods=['POST'])
def yookassa_notification():
    data = json.loads(request.data)

    with open("notifications.log", "a") as log_file:
        log_file.write(str(data) + os.linesep)

    if data['event'] == 'payment.succeeded':
        payment_info = data['object']
        payment_id = payment_info['id']

        if not is_payment_processed(payment_id):
            user_id = payment_info['metadata']['user_id']
            payment_description = payment_info['description']
            message_id = int(payment_info['metadata']['message_id'])

            gp_to_add = calculate_gp(payment_description)
            if gp_to_add not in ["week", "month", "year"]:
                add_gp(user_id, gp_to_add)
                bot2.edit_message_text(chat_id=user_id,
                                       message_id=message_id,
                                       text=f"Платеж успешно завершен! Вам начислено {gp_to_add}GP 🎉")
                log_processed_payment(payment_id)
            else:
                if gp_to_add == "week":
                    save_subs_date(user_id, create_subscription_end_date(user_id, 8))
                    bot2.edit_message_text(chat_id=user_id,
                                           message_id=message_id,
                                           text=random.choice(week_messages))
                    log_processed_payment(payment_id)
                elif gp_to_add == "month":
                    save_subs_date(user_id, create_subscription_end_date(user_id, 32))
                    bot2.edit_message_text(chat_id=user_id,
                                           message_id=message_id,
                                           text=random.choice(month_messages))
                    log_processed_payment(payment_id)
                elif gp_to_add == "year":
                    save_subs_date(user_id, create_subscription_end_date(user_id, 366))
                    bot2.edit_message_text(chat_id=user_id,
                                           message_id=message_id,
                                           text=random.choice(year_messages))
                    log_processed_payment(payment_id)

    return 'OK', 200


#------------------------------main------------------------------


dp = updater.dispatcher


#Start
start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)


#Задать вопрос
ask_question_handler = MessageHandler(Filters.regex(r"^Задать вопрос 🔍$"), handle_ask_question)
dp.add_handler(ask_question_handler)
question_handler = MessageHandler(Filters.text & (~Filters.command) & (~Filters.regex(r"^Задать вопрос 🔍$")) & (~Filters.regex(r"^Мой баланс GP 💰$")) & (~Filters.regex(r"^Купить GP 💳$")) & (~Filters.regex(r"^Возможности 🤖$")) & (~Filters.regex(r"^Очистить диалог с ботом 🧼$")) & (~Filters.regex(r"^Заработать GP 🆓$")), handle_question)
dp.add_handler(question_handler)


#Возможности 🤖
features = MessageHandler(Filters.regex(r"^Возможности 🤖$"), handle_features)
dp.add_handler(features)
dp.add_handler(CallbackQueryHandler(handle_ask_question, pattern="^ask_question$"))


#Мой баланс GP 💰
ask_my_gp = MessageHandler(Filters.regex(r"^Мой баланс GP 💰$"), my_data)
dp.add_handler(ask_my_gp)


#Заработать GP 🆓
free_gp = MessageHandler(Filters.regex(r"^Заработать GP 🆓$"), referral_code)
dp.add_handler(free_gp)


#Купить GP 💳
subscribeGPT = MessageHandler(Filters.regex(r"^Купить GP 💳$"), handle_subscribeGPT)
dp.add_handler(subscribeGPT)
dp.add_handler(CallbackQueryHandler(handle_buy_button, pattern="^buy_"))
dp.add_handler(CallbackQueryHandler(handle_subscribeGPT, pattern="^return_to_choice"))


#Очистить переписку
clear_message = MessageHandler(Filters.regex(r"^Очистить диалог с ботом 🧼$"), clear_messages)
dp.add_handler(clear_message)


#Обработка не командных сообщений
text_message_handler = MessageHandler(Filters.text & (~Filters.command) & (~Filters.regex(r"^Задать вопрос 🔍$")) & (~Filters.regex(r"^Мой баланс GP 💰$")) & (~Filters.regex(r"^Купить GP 💳$")) & (~Filters.regex(r"^Возможности 🤖$")) & (~Filters.regex(r"^Очистить диалог с ботом 🧼$")) & (~Filters.regex(r"^Заработать GP 🆓$")), handle_text_message)
dp.add_handler(text_message_handler)


#Проверка подписки
dp.add_handler(CallbackQueryHandler(handle_after_subscription, pattern="^check_subscription$"))


# Запускаем бота
updater.start_polling()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8443, ssl_context=('/etc/letsencrypt/live/skillxhub.ru/fullchain.pem', '/etc/letsencrypt/live/skillxhub.ru/privkey.pem'))

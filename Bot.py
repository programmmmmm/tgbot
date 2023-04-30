import logging
import random
import string
import threading
import time

from firebase_admin import credentials, initialize_app, db

from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import poe

clients = {}

# Токены
TELEGRAM_BOT_TOKEN = "5785989131:AAFFcu7ekjOTXiMYK5ptMuxsamNVk8i65j0" #Тестовый

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
            KeyboardButton(text="Возможности")
        ],
        [
            KeyboardButton(text="Premium-подписка")
        ],
        [
            KeyboardButton(text="Мои данные"),
            KeyboardButton(text="Очистить переписку")
        ]
    ],
    resize_keyboard=True
)

# Токены
TELEGRAM_BOT_TOKEN = "5785989131:AAFFcu7ekjOTXiMYK5ptMuxsamNVk8i65j0" #Тестовый
cred = credentials.Certificate("telegabot-16d96-firebase-adminsdk-vsi1b-ae3594244d.json")
initialize_app(cred, {'databaseURL': 'https://telegabot-16d96-default-rtdb.europe-west1.firebasedatabase.app/'})
client = poe.Client('Z2nTcuapVPT41-2IdLHnyA%3D%3D')

# БАЗА ДАННЫХ
def generate_random_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def add_new_user(user_id, random_name_bot):
    ref = db.reference(f'users/{user_id}')
    ref.set({
        'random_name_bot': random_name_bot,
        'gp': 15,
        'subscription': "none"
    })

def user_exists(user_id):
    ref = db.reference(f'users/{user_id}')
    return ref.get() is not None

def get_user_data(user_id, field):
    ref = db.reference(f'users/{user_id}/{field}')
    return ref.get()


def set_user_data(user_id, field, value):
    ref = db.reference(f'users/{user_id}/{field}')
    ref.set(value)

# Обработка команды /start
def start(update: Update, context: CallbackContext):

    user_id = update.effective_user.id

    user_data = get_user_data(user_id, "gp")
    if user_data == None:
        random_name_bot = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        add_new_user(user_id, random_name_bot)
        client.create_bot(random_name_bot, prompt="", base_model="chinchilla")
        user_data = get_user_data(user_id, 'gp')
        while user_data == None:
            print(user_data)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Я ChatGPT! Я готов ответить на любой твой вопрос! Не стесняйся, задавай!",
                             reply_markup=keyboard)

# Обработка нажатия на кнопку "Задать вопрос"
def handle_ask_question(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите ваш вопрос:")

# Обработка введенного вопроса
def handle_question(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name_bot = get_user_data(user_id, 'random_name_bot')

    threading.Thread(target=process_question,
                     args=(update, context, client, name_bot, update.message.text)).start()
    time.sleep(1)


def process_question(update: Update, context: CallbackContext, client, name_bot, message_text):
    print(name_bot)
    response = ""
    for chunk in client.send_message(name_bot, message_text):
        response += chunk["text_new"]
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)



# Добавляем обработчики команд и сообщений
start_handler = CommandHandler("start", start)
ask_question_handler = MessageHandler(Filters.regex(r"^Задать вопрос 🔍$"), handle_ask_question)
question_handler = MessageHandler(Filters.text & (~Filters.command), handle_question)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(ask_question_handler)
dispatcher.add_handler(question_handler)

# Запускаем бота
updater.start_polling()

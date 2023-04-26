import json

import time

import logging

import html2text

import threading

from typing import List

import random

import re

import traceback

import sys

import poe

import string


import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from telegram import ReplyKeyboardMarkup
from telegram import LabeledPrice, PreCheckoutQuery
from telegram.ext import PreCheckoutQueryHandler
from telegram import ChatAction
from telegram.ext import BaseFilter


payment_links = {
    "25_requests": "https://poe.com/Sage25",
    "50_requests": "https://poe.com/Sage50",
    "200_requests": "https://poe.com/Sage200",
    "1_week": "https://poe.com/Sage1Week",
    "1_month": "https://poe.com/Sage1Month",
    "1_year": "https://poe.com/Sage1Year",
}


#TELEGRAM_BOT_TOKEN = "6248465953:AAFR9gek247GVqFeo4t-LgvwI5TEA8Nr9Ao" #Рабочий
TELEGRAM_BOT_TOKEN = "5785989131:AAFFcu7ekjOTXiMYK5ptMuxsamNVk8i65j0" #Тестовый

def remove_emoji(text: str) -> str:
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002500-\U00002BEF"  # chinese characters
                           u"\U00002702-\U000027B0"
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           u"\U0001f926-\U0001f937"
                           u"\U00010000-\U0010ffff"
                           u"\u2640-\u2642"
                           u"\u2600-\u2B55"
                           u"\u200d"
                           u"\u23cf"
                           u"\u23e9"
                           u"\u231a"
                           u"\ufe0f"  # dingbats
                           u"\u3030"
                           "]+", re.UNICODE)

    return emoji_pattern.sub(r'', text)


client = poe.Client('Z2nTcuapVPT41-2IdLHnyA%3D%3D')

def generate_random_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def send_message_and_get_response_to_user_question(message):
    random_name_bot = generate_random_name()
    client.create_bot(random_name_bot, prompt="", base_model="chinchilla")
    response = ""
    for chunk in client.send_message(random_name_bot, message):
        response += chunk["text_new"]
    return response


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def add_new_user_if_not_exists(user_id, conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user_exists = cur.fetchone()
    if not user_exists:
        initial_gp = 15
        cur.execute("INSERT INTO users (user_id, gp) VALUES (%s, %s)", (user_id, initial_gp))
        conn.commit()
    cur.close()


def start(update: Update, context: CallbackContext):
    keyboard = [
        ["Задать вопрос 🔍", "Возможности"],
        ["Premium-подписка"], ["Мои данные"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    update.message.reply_text("Привет! Я ChatGPT! Я готов ответить на любой твой вопрос! Не стесняйся, задавай!",
                              reply_markup=reply_markup)





def is_user_subscribed(bot, user_id, channel_username):
    try:
        chat_member = bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        return chat_member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

def handle_check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query

    if check_subscription(update, context):
        query.edit_message_text("Спасибо за подписку! Теперь вы можете задать вопрос.")
    else:
        query.answer("Пожалуйста, подпишитесь на канал и нажмите кнопку 'Проверить подписку' еще раз.")


def check_subscription(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    channel_username = '@NeuroNewsGpt'

    if is_user_subscribed(context.bot, user_id, channel_username):
        return True
    else:
        return False


def get_user_data(user_id, user_data):
    if user_id not in user_data:
        user_data[user_id] = {'gp': 100}
    return user_data[user_id]

def update_user_data(user_id, chat_data, updated_data):
    chat_data[user_id].update(updated_data)


def my_data(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id, context.user_data)
    update.message.reply_text(f"Ваш тарифный план: {user_data['gp']}GP")


def handle_menu(update: Update, context: CallbackContext):
    user_message = update.message.text
    if user_message == "Задать вопрос 🔍":
        if check_subscription(update, context):
            context.user_data["ready_to_ask"] = True
            update.message.reply_text("Пожалуйста, задай свой вопрос.")
        else:
            # Текст, который будет отправлен, если пользователь не подписан
            update.message.reply_text("Чтобы задать вопрос, пожалуйста, подпишитесь на наш канал @NeuroNewsGpt",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("Подписаться", url="https://t.me/NeuroNewsGpt"),
                                           InlineKeyboardButton("Проверить подписку", callback_data="check_subscription")]]))
    elif user_message == "Возможности":
        context.bot.send_message(chat_id=update.effective_chat.id, text="<b>🔥 Я помогу тебе:</b>\n\n"
                                                                        "1️⃣ создать резюме\n\n"
                                                                        "2️⃣ написать текст\n\n"
                                                                        "3️⃣ перевести иностранный текст\n\n"
                                                                        "4️⃣ ответить на вопросы\n\n"
                                                                        "5️⃣ написать и отладить код\n\n"
                                                                        "6️⃣ спланировать питание для похудения\n\n"
                                                                        "💡Это лишь малая часть моего функционала. Задавай мне любые задачи, а я постараюсь тебе помочь.\n\n"
                                                                        "Нажми 'Задать вопрос 🔍' ниже, чтобы начать общение со мной. 👇🏻",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Задать вопрос 🔍", callback_data="ask_question")]]), parse_mode=telegram.ParseMode.HTML)
    elif user_message == "Premium-подписка":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Доступно 10 запросов. Здесь вы можете посмотреть, какое количество запросов и за какую сумму вы можете приобрести!",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton("25шт - 19р", callback_data="25_requests"),
                                      InlineKeyboardButton("50шт - 35р", callback_data="50_requests")],
                                     [InlineKeyboardButton("200шт - 119р", callback_data="200_requests"),
                                      InlineKeyboardButton("1 неделя - 199р", callback_data="1_week")],
                                     [InlineKeyboardButton("1 месяц - 549р", callback_data="1_month"),
                                      InlineKeyboardButton("1 год - 1149р", callback_data="1_year")],
                                 ]))
    elif user_message == "Мои данные":
        my_data(update, context)
    else:
        if "ready_to_ask" in context.user_data:
            context.user_data["ready_to_ask"] = False


def handle_inline_keyboard_button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data

    if callback_data == "ask_question":
        context.user_data["ready_to_ask"] = True
        query.edit_message_text("Пожалуйста, задай свой вопрос.")
    elif callback_data in payment_links:
        payment_link = payment_links[callback_data]
        query.edit_message_text(f"Для оплаты перейдите по ссылке: {payment_link}")
    else:
        query.answer("Неизвестное действие.")


def ask_question(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id, context.user_data)

    if context.user_data.get("ready_to_ask"):
        if user_data['gp'] > 0:
            context.user_data["ready_to_ask"] = True
            if context.user_data.get("ready_to_ask"):
                user_message = update.message.text

                # Создаем список сообщений для анимации загрузки
                loading_messages = [
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
                    "Активирую глобальный поиск знаний... 🌎"
                ]

                loading_message = random.choice(loading_messages)

                def send_typing_animation(update, context, loading_messages, delay, random_choice=False):
                    loading_msg = context.bot.send_message(chat_id=update.effective_chat.id, text=loading_messages[0])

                    prev_loading_message = None
                    while not context.user_data.get("stop_loading"):
                        if random_choice:
                            loading_message = random.choice(loading_messages)
                        else:
                            loading_message = loading_messages.pop(0)
                            loading_messages.append(loading_message)

                        # Проверка, отличается ли новое сообщение от предыдущего
                        if loading_message != prev_loading_message:
                            try:
                                context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                              message_id=loading_msg.message_id,
                                                              text=loading_message)
                                prev_loading_message = loading_message  # Обновление предыдущего сообщения
                            except telegram.error.BadRequest as e:
                                logger.warning(f"Failed to edit message: {e}")
                        else:
                            logger.warning("New message is the same as the previous one. Skipping.")

                        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
                        time.sleep(delay)

                context.user_data['stop_loading'] = False  # Сбрасываем значение перед каждым вопросом

                # Создаем и запускаем поток для отправки анимации загрузки
                loading_thread = threading.Thread(target=send_typing_animation,
                                                  args=(update, context, loading_messages, 2, True))
                loading_thread.start()

                # Здесь вызываем функцию для работы с WebDriver и отправки сообщения на сайт
                cleaned_user_message = remove_emoji(user_message)
                response = send_message_and_get_response_to_user_question(cleaned_user_message)

                context.user_data['stop_loading'] = True  # Останавливаем анимацию загрузки
                loading_thread.join()  # Ждем завершения потока с анимацией загрузки

                # Удаляем сообщение с анимацией загрузки
                try:
                    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id + 1)
                except Exception as e:
                    logger.warning(f"Failed to delete loading message: {e}")

                context.bot.send_message(chat_id=update.effective_chat.id, text=response)
                context.user_data["ready_to_ask"] = False

            else:
                update.message.reply_text("Если вы хотите задать у меня вопрос, то нажимайте на кнопку в меню 'Задать вопрос'! И я с удовольствием отвечу вам.")

            context.user_data[user_id]['gp'] -= 1

        else:
            update.message.reply_text("У вас недостаточно GP для совершения запроса. Пожалуйста, пополните баланс.")


def send_typing_animation(update: Update, context: CallbackContext, messages: List[str], delay: int,
                          loop: bool = False):
    index = 0
    chat_id = update.effective_chat.id
    message_id = None

    while not context.user_data.get('stop_loading'):
        try:
            if message_id is None:
                sent_message = context.bot.send_message(chat_id=chat_id, text=messages[index])
                message_id = sent_message.message_id
            else:
                context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=messages[index])

            time.sleep(delay)

            index += 1
            if index == len(messages):
                if loop:
                    index = 0
                else:
                    break
        except Exception as e:
            logger.warning(f"Failed to send or edit typing animation: {e}")
            break


def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex('^Задать вопрос 🔍$'), handle_menu))
    dp.add_handler(MessageHandler(Filters.regex('^Возможности$'), handle_menu))
    dp.add_handler(MessageHandler(Filters.regex('^Premium-подписка$'), handle_menu))
    dp.add_handler(MessageHandler(Filters.regex('^Мои данные$'), handle_menu))

    dp.add_handler(CallbackQueryHandler(handle_check_subscription, pattern="^check_subscription$"))
    dp.add_handler(MessageHandler(Filters.text, ask_question))
    dp.add_handler(CallbackQueryHandler(handle_inline_keyboard_button_click))
    dp.add_error_handler(error)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ask_question))


    # Запустите бота
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            # Здесь вы можете добавить отправку сообщения с ошибкой
            # например, используя функцию send_message
            # send_message(chat_id, f"Произошла ошибка: {str(e)}")
            print(f"Произошла ошибка: {str(e)}")
            print("Перезапуск бота через 5 секунд...")
            time.sleep(5)

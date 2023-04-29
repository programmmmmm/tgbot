import time

import logging

import threading

from typing import List

import random

import poe

import string

from firebase_admin import credentials, initialize_app, db

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, LabeledPrice, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext, PreCheckoutQueryHandler

TELEGRAM_BOT_TOKEN = "6224095953:AAFR9gek247GVqFeo4t-LgvwI5KOB8Nr9Ao" #Рабочий

client = poe.Client('Z2nTtrapVPT41-2IdLHnyA%3D%3D')

cred = credentials.Certificate("telegabot-16d96-firebase-adminsdk-vsi1b-ae3496034d.json")
initialize_app(cred, {'databaseURL': 'https://telegabot-16d96-default-rtdb.europe-west1.firebasedatabase.app/'})


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

def add_gp(user_id, gp_to_add):
    current_gp = get_user_data(user_id, 'gp')
    if current_gp is not None:
        new_gp = current_gp + gp_to_add
        set_user_data(user_id, 'gp', new_gp)


def send_message_and_get_response_to_user_question(update: Update, message):
    #random_name_bot = "02dc6wx6ay83t8s" #generate_random_name()
    #client.create_bot(random_name_bot, prompt="", base_model="chinchilla")
    user_id = update.effective_user.id
    name_bot = get_user_data(user_id, 'random_name_bot')
    print(name_bot)
    response = ""
    for chunk in client.send_message(name_bot, message):  # random_name_bot, message):
        response += chunk["text_new"]

    return response


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    keyboard = [
        ["Задать вопрос 🔍", "Возможности"],
        ["Premium-подписка"], ["Мои данные"], ["Отчистить переписку"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    user_id = update.effective_user.id

    user_data = get_user_data(user_id, "gp")
    if user_data == None:
        random_name_bot = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        add_new_user(user_id, random_name_bot)
        client.create_bot(random_name_bot, prompt="", base_model="chinchilla")
        user_data = get_user_data(user_id, 'gp')
        while user_data == None:
            print(user_data)

    update.message.reply_text("Привет! Я ChatGPT! Я готов ответить на любой твой вопрос! Не стесняйся, задавай!",
                              reply_markup=reply_markup)


def new_bot(user_id):
    random_name_bot = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
    client.create_bot(random_name_bot, prompt="", base_model="chinchilla")
    ref = db.reference(f'users/{user_id}')
    ref.update({
        'random_name_bot': random_name_bot,
    })


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


def update_user_data(user_id, chat_data, updated_data):
    chat_data[user_id].update(updated_data)


def my_data(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id, context.user_data)
    current_gp = get_user_data(user_id, 'gp')
    update.message.reply_text(f"Ваш тарифный план: {current_gp}GP")



def handle_menu(update: Update, context: CallbackContext):
    user_message = update.message.text

    user_id = update.message.from_user.id
    user_data = get_user_data(user_id, 'gp')
    if user_data == None:
        random_name_bot = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        add_new_user(user_id, random_name_bot)
        client.create_bot(random_name_bot, prompt="", base_model="chinchilla")
        user_data = get_user_data(user_id, 'gp')
        while user_data == None:
            print(user_data)

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
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Доступно 10 запросов. Здесь вы можете посмотреть, какое количество запросов и за какую сумму вы можете приобрести!",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton("120GP - 60 руб.", callback_data="pay_60")],
                                     [InlineKeyboardButton("200GP - 119р", callback_data="pay_119")],
                                     [InlineKeyboardButton("1 неделя - 199р", callback_data="pay_199")],
                                     [InlineKeyboardButton("1 месяц - 549р", callback_data="pay_549")],
                                     [InlineKeyboardButton("1 год - 1149р", callback_data="pay_1149")],
                                 ]))
    elif user_message == "Мои данные":
        my_data(update, context)

    elif user_message == "Отчистить переписку":
        new_bot(user_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Переписка очищена", parse_mode=telegram.ParseMode.HTML)
    else:
        if "ready_to_ask" in context.user_data:
            context.user_data["ready_to_ask"] = False


def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data.startswith("pay_"):
        amount = query.data.split("_")[1]
        price = int(amount) * 100
        prices = [LabeledPrice("Стоимость", price)]

        context.bot.send_invoice(chat_id=query.from_user.id,
                                 title="Оплата",
                                 description="Оплата услуги",
                                 payload="custom_payload",
                                 provider_token="795840012:LIVE:22800",
                                 # Замените этот токен на тот, что вы получили от BotFather
                                 currency="RUB",
                                 prices=prices,
                                 start_parameter="payment",
                                 provider_data='{"shopId": "312766", "shopArticleId": "0"}',
                                 # Замените значения shopId и shopArticleId на свои
                                 )

def handle_pre_checkout_query(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    if query.invoice_payload == "custom_payload":
        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
    else:
        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False, error_message="Что-то пошло не так.")

def calculate_gp(amount):
    if amount == 6000:
        return 120
    elif amount == 11900:
        return 200
    # Добавьте другие условия для различных стоимостей, если необходимо


def handle_successful_payment(update: Update, context: CallbackContext):
    successful_payment = update.message.successful_payment
    user_id = update.message.from_user.id
    total_amount = successful_payment.total_amount
    gp_to_add = calculate_gp(total_amount)  # Функция для расчета GP на основе стоимости

    add_gp(user_id, gp_to_add)  # Функция для добавления GP пользователю
    context.bot.send_message(chat_id=user_id, text=f"Платеж успешно завершен! Вам начислено {gp_to_add} GP.")


def handle_inline_keyboard_button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data

    if callback_data == "ask_question":
        context.user_data["ready_to_ask"] = True
        query.edit_message_text("Пожалуйста, задай свой вопрос.")
    else:
        query.answer("Неизвестное действие.")


def ask_question(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id, 'gp')

    if context.user_data.get("ready_to_ask"):

        if user_data > 0:
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
                response = send_message_and_get_response_to_user_question(update, user_message)

                context.user_data['stop_loading'] = True  # Останавливаем анимацию загрузки
                loading_thread.join()  # Ждем завершения потока с анимацией загрузки

                # Удаляем сообщение с анимацией загрузки
                try:
                    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id + 1)
                except Exception as e:
                    logger.warning(f"Failed to delete loading message: {e}")

                if response:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=response)
                    context.user_data["ready_to_ask"] = False
                else:
                    update.message.reply_text(
                        "Извините, возникла ошибка при отправке сообщения. Повторите свой запрос чуть позже."
                    )

            current_gp = get_user_data(user_id, 'gp')
            set_user_data(user_id, 'gp', current_gp - 1)

        else:
            update.message.reply_text("У вас недостаточно GP для совершения запроса. Пожалуйста, пополните баланс.")
    else:
        update.message.reply_text(
            "Если вы хотите задать у меня вопрос, то нажимайте на кнопку в меню 'Задать вопрос'! И я с удовольствием отвечу вам.")

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

    dp.add_handler(CallbackQueryHandler(handle_callback_query))

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex('^Задать вопрос 🔍$'), handle_menu))
    dp.add_handler(MessageHandler(Filters.regex('^Возможности$'), handle_menu))
    dp.add_handler(MessageHandler(Filters.regex('^Premium-подписка$'), handle_menu))
    dp.add_handler(MessageHandler(Filters.regex('^Мои данные$'), handle_menu))
    dp.add_handler(MessageHandler(Filters.regex('^Отчистить переписку$'), handle_menu))

    dp.add_handler(CallbackQueryHandler(handle_check_subscription, pattern="^check_subscription$"))
    dp.add_handler(MessageHandler(Filters.text, ask_question))
    dp.add_handler(CallbackQueryHandler(handle_inline_keyboard_button_click))
    dp.add_error_handler(error)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ask_question))

    dp.add_handler(PreCheckoutQueryHandler(handle_pre_checkout_query))

    dp.add_handler(MessageHandler(Filters.successful_payment, handle_successful_payment))

    # Запустите бота
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

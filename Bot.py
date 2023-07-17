# Импортируем необходимые классы
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import random # для генерации случайных чисел
import logging
import pandas as pd
import datetime

# Создаем переменную для хранения номера недели
last_week = -1

# Создаем объект Updater с токеном нашего бота
updater = Updater('5925395963:AAEtt0-hzK9eZzChdP3adjERC-_jpA3ktT8', use_context=True)

# Создаем объект Dispatcher
dispatcher = updater.dispatcher

# Загружаем данные из Excel файла в DataFrame
df = pd.read_excel('example.xlsx')

# Выбираем случайную строку из первого столбца DataFrame
def get_random_horoscope():
    # загружаем данные из файла csv
    df = pd.read_excel('example.xlsx', header=None)
    # генерируем случайное число, чтобы выбрать случайный гороскоп из датафрейма
    row_number = random.randint(0, len(df) - 1)
    # проверяем, что row_number не больше, чем количество строк в df
    if row_number >= len(df):
        row_number = len(df) - 1
    return df.iloc[row_number, 0]



# Создаем список гороскопов на неделю для каждого знака зодиака
horoscopes = {
    'овен': [
        '*♈️ Овен*\n\n'+get_random_horoscope()
    ],
    'телец': [
        '*♉️ Телец*\n\n'+get_random_horoscope()
    ],
    'близнецы': [
        '*♊️ Близнецы*\n\n'+get_random_horoscope()
    ],
    'рак': [
        '*♋️ Рак*\n\n'+get_random_horoscope()
    ],
    'лев': [
        '*♌️ Лев*\n\n'+get_random_horoscope()
    ],
    'дева': [
        '*♍️ Дева*\n\n'+get_random_horoscope()
    ],
    'весы': [
        '*♎️ Весы*\n\n'+get_random_horoscope()
    ],
    'скорпион': [
        '*♏️ Скорпион*\n\n'+get_random_horoscope()
    ],
    'стрелец': [
        '*♐️ Стрелец*\n\n'+get_random_horoscope()
    ],
    'козерог': [
        '*♑️ Козерог*\n\n'+get_random_horoscope()
    ],
    'водолей': [
        '*♒️ Водолей*\n\n'+get_random_horoscope()
    ],
    'рыба': [
        '*♓️ Рыбы*\n\n'+get_random_horoscope()
    ]
}


# Настройка логирования ошибок
logging.basicConfig(filename='errors.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s')

def handle_exceptions(func):
    def wrapper(update, context):
        try:
            return func(update, context)
        except Exception as e:
            # Обработка ошибки
            error_message = '*Упс... у нас возникла ошибка... 🤖*\n\nМы боты, но даже мы не всегда идеальны! Но не расстраивайтесь, подождите немного времени и повторите свой запрос. А может, пока мы здесь устраняем неполадки, вы можете попить чаю или съесть что-нибудь вкусненькое? Всё наладится, мы обещаем!'
            context.bot.send_message(chat_id=update.effective_chat.id, text=error_message, parse_mode="Markdown")
            logging.error(f'Ошибка при выполнении команды {func.__name__}: {e}', exc_info=True)
    return wrapper


# Создаем функцию для проверки подписки пользователя на канал
@handle_exceptions
def check_subscription(update, context):
    # Получаем список каналов, на которые подписан пользователь
    channels = context.bot.get_chat_member('@dusha_star', update.effective_chat.id)
    # Если пользователь подписан на канал, то возвращаем True
    if channels.status in ['creator', 'administrator', 'member']:
        print("Да")
        return True
    # Если пользователь не подписан на канал, то возвращаем False
    else:
        print("Нет")
        return False


# Создаем глобальную переменную для хранения объекта message
global message

# Создаем функцию для отправки сообщения с просьбой подписаться на канал
@handle_exceptions
def send_subscription_request(update, context):
    # Создаем inline клавиатуру с двумя кнопками - Подписаться и Проверка подписки
    keyboard = telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton('Подписаться ✅', url='https://t.me/dusha_star')], [telegram.InlineKeyboardButton('Проверка подписки 🔍', callback_data='check_subscription')]])
    # Отправляем сообщение с клавиатурой и сохраняем его в глобальную переменную message
    global message
    message = context.bot.send_message(chat_id=update.effective_chat.id, text='*Приветствую тебя, путник!* 🙋‍♂️\n\nТы попал в мир астрологии, где я, твой верный Астробот, могу прислать тебе гороскоп на неделю по твоему знаку зодиака.\n\nНо прежде чем мы начнем наше путешествие, я прошу тебя сделать одно маленькое дело - подпишись на канал "Звёзды в душе" и получи доступ к мудрости звезд! ✨', reply_markup=keyboard, parse_mode="Markdown")


# Создаем функцию для обработки нажатий на inline кнопки
@handle_exceptions
def callback(update, context):
    # Получаем данные из callback_query
    query = update.callback_query
    # Если пользователь нажал на кнопку Проверка подписки, то проверяем, подписан ли он на канал
    if query.data == 'check_subscription':
        # Проверяем, подписан ли пользователь на канал
        if check_subscription(update, context):
            # Если подписан, то изменяем сообщение бота с благодарностью за подписку на канал
            # Для этого используем глобальную переменную message
            global message
            # Изменяем текст сообщения бота с помощью метода bot.edit_message_text
            # Передаем ему параметры chat_id, message_id и text
            context.bot.edit_message_text(chat_id=message.chat_id,
                                          message_id=message.message_id,
                                          text='*Спасибо за подписку*🙏\n\nТеперь ты можешь получать гороскоп на неделю по твоему знаку зодиака. Для этого просто напиши мне свой знак в чате. Например, "Овен" или "Весы".\n\nЖелаю тебе удачи и счастья! ✨', parse_mode="Markdown")
        else:
            # Если не подписан, то отправляем ему уведомление об этом
            context.bot.answer_callback_query(query.id, 'Ты еще не подписался на телеграм канал! 😞')


# Создаем функцию для отправки сообщения с благодарностью за подписку на канал
@handle_exceptions
def send_subscription_thanks(message):
    # Отправляем сообщение с благодарностью
    print("Я тут")
    message.reply_text('Спасибо, что подписался на канал "Звёзды в душе"! 🙏\n\nТеперь ты можешь получать гороскоп на неделю по твоему знаку зодиака. Для этого просто напиши мне свой знак в чате. Например, "Овен" или "Весы".\n\nЖелаю тебе удачи и счастья! ✨', parse_mode="Markdown")

# Создаем функцию для обработки команды /start
@handle_exceptions
def start(update, context):
    # Проверяем, подписан ли пользователь на канал
    if check_subscription(update, context):
        # Если подписан, то отправляем ему приветственное сообщение без клавиатуры
        context.bot.send_message(update.effective_chat.id, '*Здравствуй, путник!* 🙋‍♂️\n\nЯ твой Астробот, и я могу рассказать тебе гороскоп на неделю по твоему знаку зодиака.\n\nНапиши свой знак зодиака (например: Рак) и я отвечу тебе гороскопом на неделю!', parse_mode="Markdown")
    else:
        # Если не подписан, то отправляем ему сообщение с просьбой подписаться на канал
        send_subscription_request(update, context)


# Создаем функцию для обработки текстовых сообщений
@handle_exceptions
def text(update, context):
    global last_week
    global last_day
    # Получаем текст сообщения от пользователя
    keyboard = telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton('Посетить канал 💫', url='https://t.me/dusha_star')]])
    keyboard2 = telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton('Ежедневный гороскоп ✨', url='https://t.me/dusha_star')]])
    text = update.effective_message.text
    whoIam = "*Бип...Пуп... Кто...Я? 🤖*\n\nЯ твой Астробот! Всегда готов написать гороскоп на всю неделю! Но помни, что я всего лишь машина, хоть и очень умная. Пиши свой знак зодиака, а я пришлю тебе гороскоп!\n\nЕсли тебе нужна тёплая атмосфера и общение с настоящими людьми, то рекомендую зайти в наш телеграм канал. Там публикуются ежедневные гороскопы и интереснейшие посты. Подписывайся и будь в курсе всех звёздных событий!"
    # Проверяем, подписан ли пользователь на канал
    if check_subscription(update, context):
        # Если подписан, то проверяем, написал ли он свой знак зодиака
        if text.lower() in horoscopes:
            # Создаем список гороскопов для каждого знака зодиака
            sign_emojis = {
                'овен': '♈️',
                'телец': '♉️',
                'близнецы': '♊️',
                'рак': '♋️',
                'лев': '♌️',
                'дева': '♍️',
                'весы': '♎️',
                'скорпион': '♏️',
                'стрелец': '♐️',
                'козерог': '♑️',
                'водолей': '♒️',
                'рыба': '♓️'
            }

            # Создаем список гороскопов для каждого знака зодиака
            for sign in sign_emojis:
                horoscopes[sign] = [
                    f'*{sign_emojis[sign]} {sign.capitalize()}*\n\n{get_random_horoscope()}'
                ]
            # Получаем текущий номер недели
            today_week = datetime.datetime.now().isocalendar()[1]

            # Проверяем, изменился ли номер недели - То есть если 28 неделя не равна 29(То есть как бы прошла уже неделя), то отправляем
            if today_week != last_week or text.lower() not in context.user_data.get('znak', []):
                # Если да, то выбираем случайный гороскоп из списка для данного знака зодиака
                horoscope = random.choice(horoscopes[text.lower()])
                # Отправляем пользователю гороскоп
                context.bot.send_message(update.effective_chat.id, horoscope+"\n\nНо помните, что звезды каждый день приносят новые вызовы и возможности. Если вы хотите знать подробный гороскоп на каждый день, то заходите в наш телеграм канал почаще!\n\nКнопочка для перехода внизу ⤵️", parse_mode="Markdown", reply_markup=keyboard2)

                #То есть как бы если прошла неделя, то есть 28 неделя не равна 29, то очищаем список!
                if today_week != last_week:
                    # Если да, то очищаем список znak в context.user_data
                    context.user_data['znak'] = []
                # Добавляем знак зодиака пользователя в список znak в context.user_data
                if 'znak' not in context.user_data:
                    # Если ключа 'znak' нет в context.user_data, то создаем его и присваиваем ему пустой список
                    context.user_data['znak'] = []
                context.user_data['znak'].append(text.lower())
                print(context.user_data['znak'])

                # Сохраняем текущий номер недели в переменную
                last_week = today_week

            else:
                znaki_zodiaka = {
                    'овен': '*"Овна"*',
                    'телец': '*"Тельца"*',
                    'близнецы': '*"Близнеца"*',
                    'рак': '*"Рака"*',
                    'лев': '*"Льва"*',
                    'дева': '*"Девы"*',
                    'весы': '*"Весов"*',
                    'скорпион': '*"Скорпиона"*',
                    'стрелец': '*"Стрельца"*',
                    'козерог': '*"Козерога"*',
                    'водолей': '*"Водолея"*',
                    'рыба': '*"Рыбы"*'
                }

                # Задаем искомый ключ
                key = text.lower()

                # Получаем значение по ключу, используя квадратные скобки
                value = znaki_zodiaka[key]
                # Если нет, то отправляем сообщение, что гороскоп уже был отправлен
                context.bot.send_message(update.effective_chat.id, "*Стоп, стоп, стоп… *🙃\n\nНе торопись, путник, ты уже знаешь судьбу для "+value+" на эту неделю. Не пытайся изменить ее, а лучше подготовься к ней. Или хочешь посмотреть, что ждет твоих друзей по знакам зодиака? Тогда пиши мне другой знак, а новый гороскоп для тебя будет готов в понедельник!\n\nА пока ты можешь посетить наш телеграм канал и узнать ежедневный гороскоп. Кнопочка для перехода внизу ⤵️", reply_markup=keyboard2, parse_mode="Markdown")
        elif "кто ты" in text.lower():
            context.bot.send_message(update.effective_chat.id, whoIam, parse_mode="Markdown", reply_markup=keyboard)
        elif "ты кто" in text.lower():
            context.bot.send_message(update.effective_chat.id, whoIam, parse_mode="Markdown", reply_markup=keyboard)
        elif text.lower() == "/start":
            start(update, context)

        # Если написал что-то другое, то отправляем ему сообщение, что мы не понимаем его
        else:
            context.bot.send_message(update.effective_chat.id,
                                     '*Прости, путник, я не понимаю тебя* 🤷‍♂️\n\nПожалуйста, напиши свой знак зодиака!',
                                     parse_mode="Markdown")

    else:
        # Если не подписан, то отправляем ему сообщение с просьбой подписаться на канал
        send_subscription_request(update, context)


# Добавляем обработчик для callback-функции
dispatcher.add_handler(CallbackQueryHandler(callback))

# Добавляем MessageHandler для обработки текстовых сообщений
dispatcher.add_handler(MessageHandler(Filters.text, text))

# Добавляем CommandHandler для команды /start
dispatcher.add_handler(CommandHandler("start", start))

# Запускаем бота
updater.start_polling()

# Останавливаем бота при нажатии Ctrl+C
updater.idle()

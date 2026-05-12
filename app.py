import telebot
from flask import Flask
import threading
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ---------- ШАГИ КВЕСТА ----------
STEPS = [
    {
        "keyword": "1947",
        "photo": "photos/step1.png",
        "caption": "Верно! Быстрое начало! Держи подсказку, найди граффити рядом с этим местом и не забудь сфотографировать)📸\n\n"
        "Вопрос №2 Как зовут декана нашего факультета? Напиши ФИО полностью"
    },
    {
        "keyword": "зазыкин андрей вячеславович",
        "photo": "photos/step2.png",
        "caption": "Отлично! Еще годик поучись)📚\n\n"
        "Вопрос №3 Сколько кафедр на факультете? Напиши цифрой"
    },
    {
        "keyword": "3",
        "photo": "photos/step3.png",
        "caption": "Правильно! Вот следующая подсказка. Ищи дальше 🔍\n\n"
        "Вопрос №4 Как зовут председателя нашего факультета? Напиши имя и фамилию"
    },
    {
        "keyword": "руслан таукенов",
        "photo": "photos/step4.png",
        "caption": "Да это наш БОСС😎\n\n"
        "Дальше вопросы будут сложнее, поэтому нужно выбрать правильный ответ\n\n"
        "Вопрос №5 Правопреемником какого института стал автомобильно-дорожный факультет?\n"
        "1) Ленинградский автодорожный институт\n"
        "2) Ленинградский институт автомобильного транспорта и дорожного хозяйства\n"
        "3) Ленинградский автомобильно-дорожный технический институт\n"
    },
    {
        "keyword": "1",
        "photo": "photos/step5.png",
        "caption": "Правильно! Ты всё ближе к цели 🎯\n\n"
        "Вопрос №6 На какие два факультета был разделён АДФ в 1972 году?\n"
        "1) Дорожно-транспортный и механический факультет \n"
        "2) Факультеты механики и дорожной инфраструктуры\n"
        "3) Дорожно-строительный и механический факультет\n"
    },
    {
        "keyword": "3",
        "photo": "photos/step6.png",
        "caption": "Круто! Последний рывок 🏁\n\n"
        "Вопрос №7 Первое название СПбГАСУ?\n"
        "1) Ленинградский институт гражданских инженеров\n"
        "2) Институт гражданских инженеров императора Николая 1\n"
        "3) Строительное училище\n"
    },
    {
        "keyword": "2",
        "photo": "photos/step7.png",
        "caption": "Да! Ты прошел квест! Поздравляем!🎉\n\n"
        "Теперь тебе нужно составить слово по следующему алгоритму, и отправить его в форме https://forms.yandex.ru/u/6a028749f47e73bab7e2929d\n"
        "1 слово - 1-я буква\n"
        "2 слово - 2-я буква\n"
        "3 слово - 6-я буква\n"
        "4 слово - 3-я буква\n"
        "5 слово - 5-я буква\n"
        "6 слово - 10-я буква\n"
        "7 слово - 3-я буква\n"
        "8 слово - 4-я буква\n"
    }
]

user_states = {}

# ---------- ОБРАБОТЧИКИ БОТА ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_states[message.from_user.id] = 0
    bot.reply_to(message,
        f"Привет, {message.from_user.first_name}! 🕵️\n"
        "Это квест про Автомобильно-Дорожный факультет. Скорее пройди его, чтобы проверить свои знания и поучаствовать в розыгрыше призов\n\n"
        "Что нужно, чтобы успешно пройти квест? Вот 5 шагов:\n"
        "1) Ответить на вопрос\n"
        "2) Узнать и прийти на место загаданное на фотографии\n"
        "3) Найти на месте граффити\n"
        "4) Сфотографировать слово, они пригодятся в конце\n"
        "5) Составить слово и отправить его в форму\n\n"
        "И еще одно важное уточнение: станции нужно проходить строго по порядку иначе не сможешь получить итоговое слово\n\n"
        "Попробуй прямо сейчас! Найди здесь графити, оно будет первым, а после ответь на вопрос\n\n"
        "Вопрос №1 Напиши год основания нашего факультета\n"
    )

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):
    uid = message.from_user.id
    text = message.text.strip()
    if uid not in user_states:
        bot.reply_to(message, "Нажми /start, чтобы начать квест.")
        return
    cur = user_states[uid]
    if cur >= len(STEPS):
        bot.reply_to(message, "🎉 Поздравляю! Ты прошёл весь квест!")
        return
    step = STEPS[cur]
    if text.lower() == step["keyword"].lower():
        try:
            with open(step["photo"], 'rb') as f:
                bot.send_photo(message.chat.id, f, caption=step.get("caption", ""))
        except FileNotFoundError:
            bot.reply_to(message, "⚠️ Фотография не найдена.")
            return
        user_states[uid] = cur + 1
        if user_states[uid] == len(STEPS):
            bot.reply_to(message, "Последний этап пройден! Ты молодец!")
    else:
        bot.reply_to(message, "❌ Неверно. Подумай ещё! Или проверь форму записи")

# ---------- ВЕБ-СЕРВЕР ДЛЯ RENDER ----------
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    print("Бот запущен...")
    bot.remove_webhook()
    threading.Thread(target=bot.polling, kwargs={"none_stop": True}).start()
    run_flask()

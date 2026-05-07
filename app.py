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
        "photo": "photos/step1.jpg",
        "caption": "Верно! Быстрое начало!"
    },
    {
        "keyword": "зазыкин андрей вячеславович",
        "photo": "photos/step2.jpg",
        "caption": "Отлично! Еще годик поучись)"
    },
    {
        "keyword": "3",
        "photo": "photos/step3.jpg",
        "caption": "Правильно! Вот следующая подсказка. Ищи дальше 🔍"
    },
    {
        "keyword": "руслан таукенов",
        "photo": "photos/step4.jpg",
        "caption": "Да это наш БОСС"
    },
    {
        "keyword": "1",
        "photo": "photos/step5.jpg",
        "caption": "Правильно! Ты всё ближе к цели 🎯"
    },
    {
        "keyword": "3",
        "photo": "photos/step6.jpg",
        "caption": "Круто! Ты уже близко к завершению!"
    },
    {
        "keyword": "2",
        "photo": "photos/step7.jpg",
        "caption": "Правильно! Последний рывок 🏁"
    }
]

user_states = {}

# ---------- ОБРАБОТЧИКИ БОТА ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_states[message.from_user.id] = 0
    bot.reply_to(message,
        f"Привет, {message.from_user.first_name}! 🕵️\n"
        "Это квест про Автомобильно-Дорожный факультет. Скорее пройди его чтобы поучаствовать в розыгрыше BMW Али\n"
        "Как только пришлёшь правильное слово, я отправлю фото со следующей подсказкой.\n"
        "Попробуй прямо сейчас – введи кодовое слово первого этапа."
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
            bot.reply_to(message, "Последний этап пройден! Отправь любое сообщение для финала.")
    else:
        bot.reply_to(message, "❌ Неверно. Подумай ещё!")

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

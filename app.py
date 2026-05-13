import telebot
from telebot import types
from flask import Flask
import threading
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ---------- ШАГИ КВЕСТА ----------
STEPS = [
    {
        "keyword": "дороги",
        "photo": "photos/step1.png",
        "caption": "Верно! Быстрое начало! Держи подсказку, найди слово на стенде рядом с этим местом 📸\n\n"
    },
    {
        "keyword": "автомобиль",
        "photo": "photos/step2.png",
        "caption": "Отлично! Реши пример чтобы узнать номер аудитории📚\n\n"
    },
    {
        "keyword": "механика",
        "photo": "photos/step3.png",
        "caption": "Правильно! Вот следующая подсказка. Ищи дальше 🔍\n\n"
    },
    {
        "keyword": "инженер",
        "photo": "photos/step4.png",
        "caption": "Да, ты просто БОСС😎\n\n"
    },
    {
        "keyword": "тоннель",
        "photo": "photos/step5.png",
        "caption": "Правильно! Ты всё ближе к цели 🎯 небольшая подсказка (это первый этаж), а еще, ищи слово рядом, в необычном месте\n\n"
    },
    {
        "keyword": "робототехника",
        "photo": "photos/step6.png",
        "caption": "Круто! Ты скоро финишируешь, используй карту ГАСУ ✅\n\n"
    },
    {
        "keyword": "двигатель",
        "photo": "photos/step7.png",
        "caption": "Ну же! Последний рывок 🏁\n\n"
    },
    {
        "keyword": "проектирование",
        "caption": "Да! Ты прошел квест! Поздравляем!🎉\n\n"
        "Теперь тебе нужно составить слово по следующему алгоритму, и отправить его в форме https://forms.yandex.ru/u/6a028749f47e73bab7e2929d\n"
        "1 слово - 1-я буква (находится напротив входа)\n"
        "2 слово - 2-я буква (столовая)\n"
        "3 слово - 6-я буква (304К)\n"
        "4 слово - 3-я буква (111К)\n"
        "5 слово - 5-я буква (205К)\n"
        "6 слово - 10-я буква (117К)\n"
        "7 слово - 3-я буква (403К) \n"
        "8 слово - 4-я буква (307К)\n"
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
        "1) Начать квест\n"
        "2) Узнать и прийти на место загаданное на фотографии\n"
        "3) Найти на месте кодовое слово (СЛОВА РАСПОЛОЖЕНЫ НА СТЕНДАХ РЯДОМ С КАБИНЕТАМИ)\n"
        "4) Отправить мне слово, чтобы я проверил\n"
        "5) Составить итоговое слово и отправить его в форму\n\n"
        "Попробуй прямо сейчас! ПЕРВОЕ СЛОВО НАХОДИТСЯ НА СТЕНДЕ НАПРОТИВ ВХОДА. Найди его и пришли мне, оно будет первым\n\n"
    )
# ---------- ОБРАБОТЧИК /help ----------
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(
        message,
        "Если вы застряли, напишите @dobriy_led.\n"
        "Чтобы начать квест заново, отправьте команду /start."
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

import time # <-- Убедитесь, что этот импорт есть в начале файла вместе с другими

# ... весь ваш предыдущий код (обработчики, веб-сервер) ...

def start_polling():
    """Функция для запуска опроса в бесконечном цикле с обработкой ошибок."""
    while True:
        try:
            print("Запуск/перезапуск опроса бота...")
            # Запускаем polling с none_stop=True, чтобы он не падал от мелких сетевых ошибок
            bot.polling(none_stop=True)
        except Exception as e:
            # Если случилась более серьёзная ошибка (например, конфликт обновлений после сна)
            print(f"Ошибка в работе бота: {e}")
            print("Перезапуск через 10 секунд...")
            bot.stop_polling()  # Всегда останавливаем предыдущий опрос перед перезапуском
            time.sleep(10)      # Даем серверам Telegram небольшой перерыв
        else:
            # Если bot.polling() завершился без ошибок (например, по команде), выходим из цикла
            print("Опрос бота планово завершён.")
            break

# Точка входа для Render
if __name__ == "__main__":
    print("Бот запущен...")
    bot.remove_webhook()
    # Запускаем наш улучшенный опрос в отдельном потоке
    polling_thread = threading.Thread(target=start_polling)
    polling_thread.daemon = True # Поток закроется вместе с основной программой
    polling_thread.start()
    # Запускаем веб-сервер Flask для поддержания Render в активном состоянии
    run_flask()




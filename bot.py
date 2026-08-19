# bot.py
import telebot
import json
import os

import config

bot = telebot.TeleBot(config.BOT_TOKEN)

def load_json(filename, default):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

stations_default = {
    "Парк Горького": {
        "word": "весна",
        "latitude": 55.7297,
        "longitude": 37.6014
    },
    "Красная площадь": {
        "word": "кремль",
        "latitude": 55.7539,
        "longitude": 37.6208
    },
    "ВДНХ": {
        "word": "космос",
        "latitude": 55.8262,
        "longitude": 37.6378
    },
    "Арбат": {
        "word": "поэт",
        "latitude": 55.7498,
        "longitude": 37.5927
    },
    "МГУ": {
        "word": "наука",
        "latitude": 55.7029,
        "longitude": 37.5309
    }
}

routes_default = {
    "1": ["Парк Горького", "ВДНХ", "Арбат", "Красная площадь", "МГУ"],
    "2": ["Арбат", "МГУ", "Парк Горького", "ВДНХ", "Красная площадь"],
    "3": ["Красная площадь", "Арбат", "МГУ", "Парк Горького", "ВДНХ"],
    "4": ["ВДНХ", "Красная площадь", "МГУ", "Арбат", "Парк Горького"],
    "5": ["МГУ", "ВДНХ", "Красная площадь", "Парк Горького", "Арбат"]
}

stations = load_json('stations.json', stations_default)
routes = load_json('routes.json', routes_default)
teams = load_json('teams.json', {})

def get_yandex_maps_link(latitude, longitude):
    return f"https://yandex.ru/maps/?pt={longitude},{latitude}&z=17&l=map"

def get_team_by_user(user_id):
    for team_num, data in teams.items():
        if user_id in data.get('users', []):
            return team_num, data
    return None, None

def get_current_station(team_data):
    idx = team_data.get('current_index', 0)
    route = routes.get(team_data['team'], [])
    if idx < len(route):
        return route[idx]
    return None

def format_station_message(station_name):
    station_info = stations.get(station_name, {})
    text = f"📍 {station_name}"
    lat = station_info.get('latitude')
    lon = station_info.get('longitude')
    if lat and lon:
        link = get_yandex_maps_link(lat, lon)
        text += f"\n🗺️ Открыть на Яндекс.Картах: {link}"
    return text

def send_route_message(team_num):
    route = routes.get(team_num, [])
    if not route:
        return "Маршрут не найден."
    idx = teams.get(team_num, {}).get('current_index', 0)
    if idx >= len(route):
        return "🎉 Все станции пройдены!"
    text = f"📍 Маршрут команды {team_num}:\n"
    for i, station in enumerate(route):
        mark = "✅" if i < idx else ("🔸" if i == idx else "⬜️")
        text += f"{mark} {i+1}. {station}\n"
    current = route[idx]
    text += f"\nТекущая станция:\n{format_station_message(current)}"
    return text

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, 
        "Привет! Я бот для квеста.\n"
        "Напиши номер твоей команды в формате: команда 2\n\n"
        "Команды:\n"
        "/progress – текущая станция\n"
        "/route – полный маршрут\n"
        "/help – помощь"
    )

@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.reply_to(message,
        "Как пользоваться:\n"
        "1. Напиши 'команда N' (например, 'команда 2')\n"
        "2. Получишь маршрут и первую станцию\n"
        "3. Найди кодовое слово на станции\n"
        "4. Отправь кодовое слово мне\n"
        "5. Получи следующую станцию\n\n"
        "Команды:\n"
        "/progress – прогресс\n"
        "/route – весь маршрут"
    )

@bot.message_handler(commands=['progress'])
def cmd_progress(message):
    user_id = message.from_user.id
    team_num, team_data = get_team_by_user(user_id)
    if not team_num:
        bot.reply_to(message, "Сначала выбери команду: напиши 'команда N'")
        return
    bot.reply_to(message, send_message(team_num))

@bot.message_handler(commands=['route'])
def cmd_route(message):
    user_id = message.from_user.id
    team_num, team_data = get_team_by_user(user_id)
    if not team_num:
        bot.reply_to(message, "Сначала выбери команду: напиши 'команда N'")
        return
    route = routes.get(team_num, [])
    idx = team_data.get('current_index', 0)
    text = f"Полный маршрут команды {team_num}:\n\n"
    for i, station in enumerate(route):
        status = "✅" if i < idx else ("🔸" if i == idx else "⬜️")
        text += f"{status} {i+1}. {station}\n"
        station_info = stations.get(station, {})
        lat = station_info.get('latitude')
        lon = station_info.get('longitude')
        if lat and lon:
            link = get_yandex_maps_link(lat, lon)
            text += f"   🗺️ {link}\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['reset'])
def cmd_reset(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "Только для админа!")
        return
    try:
        team_num = message.text.split()[1]
        if team_num in teams:
            teams[team_num]['current_index'] = 0
            teams[team_num]['completed'] = []
            save_json('teams.json', teams)
            bot.reply_to(message, f"Прогресс команды {team_num} сброшен.")
        else:
            bot.reply_to(message, "Команда не найдена.")
    except IndexError:
        bot.reply_to(message, "Укажи номер: /reset 2")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip().lower()
    team_num, team_data = get_team_by_user(user_id)
    if not team_num:
        if text.startswith("команда "):
            try:
                team_num = text.split()[1]
                if team_num not in routes:
                    bot.reply_to(message, "Нет такой команды. Доступно: " + ", ".join(routes.keys()))
                    return
                if team_num not in teams:
                    teams[team_num] = {
                        'team': team_num,
                        'users': [user_id],
                        'current_index': 0,
                        'completed': []
                    }
                else:
                    if user_id not in teams[team_num]['users']:
                        teams[team_num]['users'].append(user_id)
                save_json('teams.json', teams)
                bot.reply_to(message, f"Ты в команде {team_num}!\n\n{send_route_message(team_num)}")
                return
            except:
                bot.reply_to(message, "Напиши 'команда N', например 'команда 2'")
                return
        else:
            bot.reply_to(message, "Напиши 'команда N' для начала")
            return
    current_station = get_current_station(team_data)
    if not current_station:
        bot.reply_to(message, "Все станции пройдены! 🎉")
        return
    station_info = stations.get(current_station, {})
    expected_word = station_info.get('word', '').lower()
    if text == expected_word:
        team_data['current_index'] += 1
        team_data.setdefault('completed', []).append(current_station)
        save_json('teams.json', teams)
        bot.send_message(
            config.ADMIN_ID,
            f"✅ Команда {team_num} прошла «{current_station}».\n"
            f"Осталось: {len(routes[team_num]) - team_data['current_index']}"
        )
        next_station = get_current_station(team_data)
        if next_station:
            bot.reply_to(message,
                f"✅ Верно!\n\nСледующая станция:\n{format_station_message(next_station)}"
            )
        else:
            bot.reply_to(message, "🎉 Все станции пройдены! Поздравляю!")
    else:
        bot.reply_to(message, "❌ Неверное слово. Попробуй ещё раз.")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
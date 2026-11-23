import json
import os
import random
import time
import urllib.parse
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Храним статистику и активные раунды по chat_id
users = {}


def api_call(method, params=None):
    url = f"{API_URL}/{method}"
    if params:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(url, data=data)
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_user(chat_id):
    return users.setdefault(
        chat_id,
        {
            "points": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "secret_num": random.randint(1, 5),
        },
    )


def add_points(user, delta):
    user["points"] = max(0, user["points"] + delta)


def main_menu_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🔢 Угадай число (1–5)", "callback_data": "menu:guess"}],
            [{"text": "✂️ Камень, ножницы, бумага", "callback_data": "menu:rps"}],
            [{"text": "🧰 Сундуки с сокровищами", "callback_data": "menu:chests"}],
            [{"text": "🎲 Дуэль на кубиках", "callback_data": "menu:dice"}],
            [
                {"text": "📊 Статистика", "callback_data": "menu:stats"},
                {"text": "🔄 Сброс счёта", "callback_data": "menu:reset"},
            ],
        ]
    }


def send_help(chat_id):
    text = (
        "🎮 *Добро пожаловать в Игровой Центр!*\n\n"
        "Выбери игру кнопкой ниже или напиши команду:\n\n"
        "• `/start` или `/help` — помощь, список команд и игр\n"
        "• `/guess` — *Угадай число* (угадай от 1 до 5, +15 очков за победу)\n"
        "• `/rps` — *Камень, ножницы, бумага* (+10 очков за победу, +3 за ничью)\n"
        "• `/chests` — *Сундуки с сокровищами* (сокровища, пусто или ловушка)\n"
        "• `/dice` — *Дуэль на кубиках* (бросок 1–6 против бота, +10 за победу)\n"
        "• `/stats` — твои очки и статистика побед\n"
        "• `/reset` — обнулить очки и статистику"
    )
    api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(main_menu_keyboard()),
        },
    )


def send_stats(chat_id):
    u = get_user(chat_id)
    text = (
        "📊 *Твоя статистика*\n\n"
        f"⭐ Очки: *{u['points']}*\n"
        f"🏆 Побед: *{u['wins']}*\n"
        f"🤝 Ничьих: *{u['draws']}*\n"
        f"💥 Поражений: *{u['losses']}*"
    )
    api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(main_menu_keyboard()),
        },
    )


def reset_stats(chat_id):
    users[chat_id] = {
        "points": 0,
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "secret_num": random.randint(1, 5),
    }
    api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": "🔄 Статистика и очки сброшены до нуля!",
            "reply_markup": json.dumps(main_menu_keyboard()),
        },
    )


def start_guess(chat_id):
    u = get_user(chat_id)
    u["secret_num"] = random.randint(1, 5)
    kb = {
        "inline_keyboard": [
            [
                {"text": "1", "callback_data": "guess:1"},
                {"text": "2", "callback_data": "guess:2"},
                {"text": "3", "callback_data": "guess:3"},
                {"text": "4", "callback_data": "guess:4"},
                {"text": "5", "callback_data": "guess:5"},
            ],
            [{"text": "⬅️ В меню игр", "callback_data": "menu:help"}],
        ]
    }
    api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": f"🔢 Я загадал число от *1 до 5*! Очков сейчас: *{u['points']}*. Выбирай:",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(kb),
        },
    )


def start_rps(chat_id):
    kb = {
        "inline_keyboard": [
            [
                {"text": "🪨 Камень", "callback_data": "rps:rock"},
                {"text": "✂️ Ножницы", "callback_data": "rps:scissors"},
                {"text": "📄 Бумага", "callback_data": "rps:paper"},
            ],
            [{"text": "⬅️ В меню игр", "callback_data": "menu:help"}],
        ]
    }
    api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": "✂️ *Камень, ножницы, бумага!* Сделай свой выбор:",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(kb),
        },
    )


def start_chests(chat_id):
    kb = {
        "inline_keyboard": [
            [
                {"text": "🧰 Сундук 1", "callback_data": "chest:1"},
                {"text": "🧰 Сундук 2", "callback_data": "chest:2"},
                {"text": "🧰 Сундук 3", "callback_data": "chest:3"},
            ],
            [{"text": "⬅️ В меню игр", "callback_data": "menu:help"}],
        ]
    }
    api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": "🧰 Перед тобой *3 сундука*. Внутри могут быть сокровища или ловушка. Какой откроешь?",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(kb),
        },
    )


def start_dice(chat_id):
    kb = {
        "inline_keyboard": [
            [{"text": "🎲 Бросить кубик!", "callback_data": "dice:roll"}],
            [{"text": "⬅️ В меню игр", "callback_data": "menu:help"}],
        ]
    }
    api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": "🎲 *Дуэль на кубиках (1–6)*! Нажми кнопку, чтобы бросить кубик против бота:",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(kb),
        },
    )


def handle_message(msg):
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip().lower()

    if text in ("/start", "/help", "помощь", "меню", "привет"):
        send_help(chat_id)
    elif text in ("/guess", "число", "угадай"):
        start_guess(chat_id)
    elif text in ("/rps", "кнб", "камень"):
        start_rps(chat_id)
    elif text in ("/chests", "сундуки"):
        start_chests(chat_id)
    elif text in ("/dice", "кубик", "дуэль"):
        start_dice(chat_id)
    elif text in ("/stats", "статистика", "счёт", "счет"):
        send_stats(chat_id)
    elif text in ("/reset", "сброс"):
        reset_stats(chat_id)
    else:
        api_call(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": "Не понял команду. Напиши /help, чтобы посмотреть список команд и игр.",
                "reply_markup": json.dumps(main_menu_keyboard()),
            },
        )


def handle_callback(cb):
    cb_id = cb["id"]
    chat_id = cb["message"]["chat"]["id"]
    data = cb.get("data", "")
    u = get_user(chat_id)

    api_call("answerCallbackQuery", {"callback_query_id": cb_id})

    if data == "menu:help":
        send_help(chat_id)
    elif data == "menu:guess":
        start_guess(chat_id)
    elif data == "menu:rps":
        start_rps(chat_id)
    elif data == "menu:chests":
        start_chests(chat_id)
    elif data == "menu:dice":
        start_dice(chat_id)
    elif data == "menu:stats":
        send_stats(chat_id)
    elif data == "menu:reset":
        reset_stats(chat_id)

    elif data.startswith("guess:"):
        guess = int(data.split(":", 1)[1])
        secret = u["secret_num"]
        if guess == secret:
            u["wins"] += 1
            add_points(u, 15)
            api_call(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": f"🎉 Точно! Загадано было *{secret}*. *+15 очков!* Всего очков: *{u['points']}*.",
                    "parse_mode": "Markdown",
                },
            )
            start_guess(chat_id)
        else:
            u["losses"] += 1
            hint = "меньше" if guess > secret else "больше"
            api_call(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": f"❌ Ты выбрал *{guess}*, но загаданное число *{hint}* (было *{secret}*). Попробуй новый раунд!",
                    "parse_mode": "Markdown",
                },
            )
            start_guess(chat_id)

    elif data.startswith("rps:"):
        choice = data.split(":", 1)[1]
        names = {"rock": "🪨 Камень", "scissors": "✂️ Ножницы", "paper": "📄 Бумага"}
        beats = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
        bot_choice = random.choice(["rock", "scissors", "paper"])

        if choice == bot_choice:
            u["draws"] += 1
            add_points(u, 3)
            res = f"🤝 Ничья! Оба выбрали {names[choice]}. *+3 очка* (итого: *{u['points']}*)."
        elif beats[choice] == bot_choice:
            u["wins"] += 1
            add_points(u, 10)
            res = f"🏆 Победа! {names[choice]} бьёт {names[bot_choice]}. *+10 очков* (итого: *{u['points']}*)."
        else:
            u["losses"] += 1
            res = f"💥 Проигрыш! {names[bot_choice]} бьёт {names[choice]}. Очков: *{u['points']}*."

        api_call("sendMessage", {"chat_id": chat_id, "text": res, "parse_mode": "Markdown"})
        start_rps(chat_id)

    elif data.startswith("chest:"):
        chosen = data.split(":", 1)[1]
        outcomes = random.sample(["treasure_big", "treasure_small", "trap"], k=3)
        pick = outcomes[0]

        if pick == "treasure_big":
            u["wins"] += 1
            add_points(u, 25)
            text = f"💎 В сундуке №{chosen} лежал клад! *+25 очков* (итого: *{u['points']}*)."
        elif pick == "treasure_small":
            u["wins"] += 1
            add_points(u, 10)
            text = f"🪙 В сундуке №{chosen} нашлись монеты! *+10 очков* (итого: *{u['points']}*)."
        else:
            u["losses"] += 1
            add_points(u, -10)
            text = f"🪤 В сундуке №{chosen} сработала ловушка! *-10 очков* (итого: *{u['points']}*)."

        api_call("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
        start_chests(chat_id)

    elif data == "dice:roll":
        player_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if player_roll > bot_roll:
            u["wins"] += 1
            add_points(u, 10)
            res = (
                f"🎲 Ты выбросил *{player_roll}*, бот — *{bot_roll}*.\n"
                f"🏆 Победа! *+10 очков* (итого: *{u['points']}*)."
            )
        elif player_roll < bot_roll:
            u["losses"] += 1
            res = (
                f"🎲 Ты выбросил *{player_roll}*, бот — *{bot_roll}*.\n"
                f"💥 Бот победил! Очков: *{u['points']}*."
            )
        else:
            u["draws"] += 1
            add_points(u, 3)
            res = (
                f"🎲 Оба выбросили по *{player_roll}*!\n"
                f"🤝 Ничья! *+3 очка* (итого: *{u['points']}*)."
            )

        api_call("sendMessage", {"chat_id": chat_id, "text": res, "parse_mode": "Markdown"})
        start_dice(chat_id)


def main():
    offset = None
    deadline = time.time() + 180

    while time.time() < deadline:
        remaining = max(1, int(deadline - time.time()))
        poll_timeout = min(20, remaining)
        params = {"timeout": poll_timeout}
        if offset is not None:
            params["offset"] = offset

        try:
            res = api_call("getUpdates", params)
        except Exception as e:
            print("Ошибка опроса:", e)
            time.sleep(2)
            continue

        if not res.get("ok"):
            time.sleep(2)
            continue

        for upd in res.get("result", []):
            offset = upd["update_id"] + 1
            if "message" in upd:
                handle_message(upd["message"])
            elif "callback_query" in upd:
                handle_callback(upd["callback_query"])


if __name__ == "__main__":
    main()
                

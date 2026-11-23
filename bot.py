import json
import os
import random
import time
import urllib.parse
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Храним загаданное число и счёт для каждого чата
games = {}


def api_call(method, params=None):
    url = f"{API_URL}/{method}"
    if params:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(url, data=data)
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def start_round(chat_id):
    secret = random.randint(1, 5)
    state = games.setdefault(chat_id, {"secret": secret, "wins": 0, "attempts": 0})
    state["secret"] = secret

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "1", "callback_data": "guess:1"},
                {"text": "2", "callback_data": "guess:2"},
                {"text": "3", "callback_data": "guess:3"},
                {"text": "4", "callback_data": "guess:4"},
                {"text": "5", "callback_data": "guess:5"},
            ]
        ]
    }

    api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": (
                "Я загадал число от 1 до 5!\n"
                f"Побед: {state['wins']} | Попыток: {state['attempts']}\n"
                "Выбери кнопку:"
            ),
            "reply_markup": json.dumps(keyboard),
        },
    )


def handle_message(msg):
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip().lower()

    if text in ("/start", "/play", "игра", "привет", "старт"):
        start_round(chat_id)
    else:
        api_call(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": "Напиши /play, чтобы сыграть в «Угадай число» (от 1 до 5).",
            },
        )


def handle_callback(cb):
    cb_id = cb["id"]
    msg = cb["message"]
    chat_id = msg["chat"]["id"]
    data = cb.get("data", "")

    api_call("answerCallbackQuery", {"callback_query_id": cb_id})

    if not data.startswith("guess:"):
        return

    guess = int(data.split(":", 1)[1])
    state = games.setdefault(
        chat_id, {"secret": random.randint(1, 5), "wins": 0, "attempts": 0}
    )
    state["attempts"] += 1
    secret = state["secret"]

    if guess == secret:
        state["wins"] += 1
        result_text = (
            f"Угадал! Это было число {secret}.\n"
            f"Счёт — побед: {state['wins']}, попыток: {state['attempts']}."
        )
    else:
        hint = "меньше" if guess > secret else "больше"
        result_text = (
            f"Мимо! Ты нажал {guess}, а загадано число {hint} (было {secret}).\n"
            f"Счёт — побед: {state['wins']}, попыток: {state['attempts']}."
        )

    api_call("sendMessage", {"chat_id": chat_id, "text": result_text})
    start_round(chat_id)


def main():
    offset = None
    # Работаем около 3 минут в рамках одного запуска GitHub Actions
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
      

import json
import os
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id: int, text: str):
  url = f"{API_URL}/sendMessage"
  payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
  req = urllib.request.Request(
      url, data=payload, headers={"Content-Type": "application/json"}
  )
  with urllib.request.urlopen(req) as resp:
    return json.loads(resp.read().decode("utf-8"))


def get_updates():
  url = f"{API_URL}/getUpdates"
  with urllib.request.urlopen(url) as resp:
    return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
  updates = get_updates()
  results = updates.get("result", [])
  if not results:
    print("Сообщений пока нет. Напиши боту в Telegram и запусти снова.")
  else:
    last_update = results[-1]
    msg = last_update.get("message") or last_update.get("edited_message") or {}
    chat = msg.get("chat") or {}
    if "id" in chat:
      reply = send_message(
          chat["id"],
          "Привет! Я твой первый бот, запущенный через GitHub Actions.",
      )
      print("Ответ отправлен:", reply.get("ok"))

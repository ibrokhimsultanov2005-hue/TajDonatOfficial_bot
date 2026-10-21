import asyncio
import json
import urllib.request
import urllib.parse

# ⚠️ ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ @BotFather
TOKEN = "8617960858:AAHtIng29aj-V8uQcWFvvBvdHrMGBHcYPjM"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

# Анимированный баннер
GIF_URL = "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif"

# База данных балансов пользователей (в памяти)
user_balances = {}

def send_request(method, data=None):
    url = API_URL + method
    if data:
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded_data)
    else:
        req = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None

def send_animation(chat_id, animation_url, caption, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "animation": animation_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    return send_request("sendAnimation", data)

def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    return send_request("sendMessage", data)

def answer_callback_query(callback_query_id, text=""):
    data = {"callback_query_id": callback_query_id, "text": text}
    return send_request("answerCallbackQuery", data)

# Главное меню с кнопкой открытия Web App (Мини-приложения)
def get_main_inline_keyboard():
    return {
        "inline_keyboard": [
            # Кнопка мини-приложения (Web App) внизу
            [{"text": "📱 Открыть Мини-приложение", "web_app": {"url": "https://google.com"}}], # Здесь можно указать ссылку на твой веб-сайт донатов
            [{"text": "🛒 Каталог донатов", "callback_data": "open_catalog"}],
            [{"text": "👛 Мой кошелёк и Баланс", "callback_data": "open_wallet"}],
            [{"text": "💳 Пополнить баланс", "callback_data": "open_topup"}],
            [{"text": "👨‍💻 Связаться с поддержкой", "url": "https://t.me/TajDonatSupport"}]
        ]
    }

def get_games_inline():
    return {
        "inline_keyboard": [
            [{"text": "🔥 Free Fire", "callback_data": "game_ff"}, {"text": "🪖 PUBG Mobile", "callback_data": "game_pubg"}],
            [{"text": "🔫 Standoff 2", "callback_data": "game_so2"}, {"text": "⭐ Telegram Stars / Premium", "callback_data": "game_tg"}],
            [{"text": "⬅️ Назад в меню", "callback_data": "back_to_menu"}]
        ]
    }

def get_wallet_inline():
    return {
        "inline_keyboard": [
            [{"text": "🟢 Пополнить (Alif / DC)", "callback_data": "topup_info"}],
            [{"text": "⬅️ Назад в меню", "callback_data": "back_to_menu"}]
        ]
    }

def process_update(update):
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        uid = msg["from"]["id"]
        full_name = msg["from"].get("first_name", "Друг")
        text = msg.get("text", "")

        if uid not in user_balances:
            user_balances[uid] = 0.0

        if text == "/start":
            caption_text = (
                f"👋 **Приветствуем, {full_name}!**\n\n"
                f"🇹🇯 **TajDonat** — официальная платформа быстрых донатов в Таджикистане.\n\n"
                f"👛 **Ваш текущий баланс:** `{user_balances[uid]:.2f} TJS`\n\n"
                f"Выберите нужный раздел или откройте мини-приложение ниже 👇"
            )
            send_animation(chat_id, GIF_URL, caption_text, reply_markup=get_main_inline_keyboard())

        elif len(text) >= 3 and not text.startswith("/"):
            buy_kb = {
                "inline_keyboard": [
                    [{"text": "💎 100 Алмазов / 60 UC — 10 TJS", "callback_data": "buy_10"}],
                    [{"text": "💎 310 Алмазов / 325 UC — 30 TJS", "callback_data": "buy_30"}],
                    [{"text": "👑 Пропуск / Pass — 60 TJS", "callback_data": "buy_60"}],
                    [{"text": "⬅️ Назад в меню", "callback_data": "back_to_menu"}]
                ]
            }
            send_message(
                chat_id,
                f"🎯 **Игровой аккаунт найден!**\n\n"
                f"🆔 ID игрока: `{text}`\n"
                f"👤 Пользователь: **{full_name}**\n"
                f"👛 Баланс кошелька: **{user_balances[uid]:.2f} TJS**\n\n"
                f"Выберите пакет для мгновенной покупки:",
                reply_markup=buy_kb
            )

    elif "callback_query" in update:
        cb = update["callback_query"]
        cb_id = cb["id"]
        chat_id = cb["message"]["chat"]["id"]
        uid = cb["from"]["id"]
        data = cb["data"]

        if uid not in user_balances:
            user_balances[uid] = 0.0

        answer_callback_query(cb_id)

        if data == "open_catalog":
            send_message(
                chat_id,
                "🎮 **Выберите игру или сервис для доната:**",
                reply_markup=get_games_inline()
            )
        elif data == "open_wallet":
            send_message(
                chat_id,
                f"👛 **Ваш кошелёк TajDonat**\n\n"
                f"💰 Доступный баланс: **{user_balances[uid]:.2f} TJS**\n\n"
                f"Вы можете покупать игры в 1 клик прямо с баланса кошелька!",
                reply_markup=get_wallet_inline()
            )
        elif data == "open_topup" or data == "topup_info":
            # ⚠️ СЮДА ВПИШИ СВОИ РЕКВИЗИТЫ КОШЕЛЬКОВ И КАРТ
            send_message(
                chat_id,
                "💳 **Как пополнить баланс в TajDonat:**\n\n"
                "1️⃣ Переведите сумму в сомони (TJS) на один из наших кошельков:\n"
                "🟢 **Alif Mob (Кошелёк):** `+992 900 00 00 00` *(Твой номер)*\n"
                "🔴 **Dushanbe City:** `+992 900 00 00 00` *(Твой номер)*\n"
                "💳 **Корти Милли:** `9771 0000 0000 0000` *(Номер твоей карты)*\n\n"
                "2️⃣ После перевода отправьте скриншот чека нашему оператору: **@TajDonatSupport**\n"
                "3️⃣ Оператор зачислит сомони на ваш баланс в боте в течение 2 минут!"
            )
        elif data == "back_to_menu":
            caption_text = (
                f"🏠 **Главное меню TajDonat**\n\n"
                f"👛 Ваш баланс: `{user_balances[uid]:.2f} TJS`\n\n"
                f"Выберите действие 👇"
            )
            send_message(chat_id, caption_text, reply_markup=get_main_inline_keyboard())

        elif data.startswith("game_"):
            games = {
                "ff": "Free Fire 🔥",
                "pubg": "PUBG Mobile 🪖",
                "so2": "Standoff 2 🔫",
                "tg": "Telegram Stars ⭐"
            }
            gname = games.get(data.split("_")[1], "Игру")
            send_message(
                chat_id,
                f"✅ Вы выбрали **{gname}**\n\n"
                f"📝 Напишите в чат ваш **Player ID** (цифровой игровой айди):"
            )
        elif data.startswith("buy_"):
            price = int(data.split("_")[1])
            if user_balances[uid] >= price:
                user_balances[uid] -= price
                send_message(
                    chat_id,
                    f"✅ **Оплата прошла успешно!**\n\n"
                    f"💰 Списано с кошелька: `{price} TJS`\n"
                    f"👛 Остаток: `{user_balances[uid]:.2f} TJS`\n\n"
                    f"⚡ Заказ отправлен в обработку. Донат поступит на ваш аккаунт в течение 1-3 минут!"
                )
            else:
                send_message(
                    chat_id,
                    f"❌ **Недостаточно средств на балансе!**\n\n"
                    f"Стоимость: `{price} TJS`\n"
                    f"Ваш баланс: `{user_balances[uid]:.2f} TJS`\n\n"
                    f"Нажмите кнопку «Пополнить баланс», чтобы внести сомони через Alif или Dushanbe City!"
                )

def main():
    print("🚀 TajDonat Bot запущен с поддержкой мини-приложения и кошелька...")
    offset = 0
    while True:
        res = send_request("getUpdates", {"offset": offset, "timeout": 5})
        if res and res.get("ok"):
            for update in res.get("result", []):
                offset = update["update_id"] + 1
                process_update(update)

if __name__ == "__main__":
    main()
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

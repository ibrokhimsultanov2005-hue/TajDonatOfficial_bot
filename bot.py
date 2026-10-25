import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils import executor

# ==========================================
# 1. ВСТАВЬ СВОИ ДАННЫЕ СЮДА:8617960858:AAFSEvPkFuAvCs8uxXMyXoF0Ou7uOe63-2o
# ==========================================
API_TOKEN = '8617960858:AAFSEvPkFuAvCs8uxXMyXoF0Ou7uOe63-2o'  # Твой токен бота
ADMIN_ID = 123456789                                       # Замени на свой Telegram ID (узнать можно у @userinfobot)
WEB_APP_URL = 'https://твой_логин.github.io/tajdonat/'       # Ссылка на твое приложение на GitHub Pages

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="💎 Магазин TajDonat", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )
    
    await message.reply(
        "⚡ Привет! Это официальный бот **TajDonat**.\n\n"
        "Нажми на кнопку ниже, чтобы открыть магазин, выбрать игру, ввести ID и оформить быстрый донат!",
        parse_mode='Markdown',
        reply_markup=markup
    )

# Приём заказа из мини-приложения
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def web_app_data_handler(message: types.Message):
    data = message.web_app_data.data
    
    try:
        order = json.loads(data)
    except json.JSONDecodeError:
        await message.answer("❌ Произошла ошибка при обработке данных заказа.")
        return

    # Красивое сообщение для администратора
    order_text = (
        "🔔 **НОВЫЙ ЗАКАЗ НА ОПЛАТУ!**\n\n"
        f"🌐 **Игра:** {order.get('game')}\n"
        f"🆔 **ID Игрока:** `{order.get('playerId')}`\n"
        f"✅ **Никнейм:** `{order.get('nickname')}`\n"
        f"💎 **Пакет:** {order.get('package')}\n"
        f"💰 **К оплате:** {order.get('price')} TJS\n\n"
        f"👤 **Покупатель:** @{message.from_user.username} (ID: `{message.from_user.id}`)\n\n"
        "👉 *Проверь поступление денег на карту/кошелек и отправь донат игроку!*"
    )

    try:
        # Отправляем заказ тебе (админу)
        await bot.send_message(chat_id=ADMIN_ID, text=order_text, parse_mode='Markdown')
        # Отвечаем игроку в боте
        await message.answer("✅ Спасибо за заказ! Администратор проверяет оплату, скоро донат поступит на ваш аккаунт.")
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки заказа администратору: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

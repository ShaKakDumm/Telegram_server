from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json

app = Flask(__name__)

# Токен бота
TOKEN = "ВАШ_ТОКЕН_БОТА"
bot = Bot(token=TOKEN)

# Хранилище для статусов
user_statuses = {}

# Функция для обработки статусов через Web App
async def handle_web_app_data(update: Update, context):
    user = update.effective_user
    data = json.loads(update.message.web_app_data.data)

    if data["action"] == "set_status":
        # Сохраняем статус
        user_statuses[user.id] = {
            "name": user.full_name,
            "status": data["status"]
        }
        await update.message.reply_text(f"Ваш статус обновлён на '{data['status']}'")

    elif data["action"] == "get_table":
        # Формируем таблицу статусов
        table = [{"name": user["name"], "status": user["status"]} for user in user_statuses.values()]
        await bot.send_message(chat_id=update.effective_chat.id, text=json.dumps({"action": "update_table", "table": table}))

@app.route("/", methods=["POST"])
def webhook():
    # Получаем обновления от Telegram
    update = Update.de_json(request.get_json(), bot)

    # Обрабатываем Web App данные
    if update.message and update.message.web_app_data:
        # Используем асинхронный обработчик
        context = None
        update.message.web_app_data.data = update.message.web_app_data.data
        handle_web_app_data(update, context)

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)

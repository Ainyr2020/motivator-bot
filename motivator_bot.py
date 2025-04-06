import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue

# Словарь с задачами
user_jobs = {}

# Функция отправки мотивации
async def send_motivation(chat_id, context):
    try:
        with open("quotes.txt", encoding="utf-8") as f:
            quotes = f.readlines()
        quote = random.choice(quotes).strip() if quotes else "Файл с цитатами пуст 😔"
    except FileNotFoundError:
        quote = "Файл quotes.txt не найден ❌"
    await context.bot.send_message(chat_id=chat_id, text=f"✨ {quote}")

# Кнопки старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("💪 Получить мотивацию", callback_data="start")],
        [InlineKeyboardButton("⛔️ Стоп", callback_data="stop")]
    ]
    await update.message.reply_text("Добро пожаловать! Мотивация БРО 👇", reply_markup=InlineKeyboardMarkup(buttons))

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "start":
        await send_motivation(chat_id, context)
        stop_job(chat_id)
        job = context.job_queue.run_repeating(callback=send_motivation_job, interval=1800, first=1800, chat_id=chat_id)
        user_jobs[chat_id] = job
        await context.bot.send_message(chat_id, "Авто-мотивация запущена каждые 30 минут! 🔁")

    elif query.data == "stop":
        if stop_job(chat_id):
            await context.bot.send_message(chat_id, "Остановил мотивацию ⛔️")
        else:
            await context.bot.send_message(chat_id, "Мотивация и так не шла 😉")

# Авто-рассылка
async def send_motivation_job(context: ContextTypes.DEFAULT_TYPE):
    await send_motivation(context.job.chat_id, context)

# Остановка задачи
def stop_job(chat_id):
    job = user_jobs.pop(chat_id, None)
    if job:
        job.schedule_removal()
        return True
    return False

# Основной запуск
def main():
    app = Application.builder().token("ТВОЙ ТОКЕН").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен ✅")
    app.run_polling()

if __name__ == "__main__":
    main()

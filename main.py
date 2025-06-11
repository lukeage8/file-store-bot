# main.py

import os
from flask import Flask, send_from_directory
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import threading, asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_URL = os.environ.get("BOT_URL")
SAVE_FOLDER = "files"
os.makedirs(SAVE_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/file/<filename>')
def serve_file(filename):
    return send_from_directory(SAVE_FOLDER, filename)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1] or update.message.video
    if not file:
        await update.message.reply_text("Please send a file.")
        return
    tg_file = await context.bot.get_file(file.file_id)
    filename = f"{file.file_unique_id}_{file.file_name if hasattr(file, 'file_name') else 'file'}"
    filepath = os.path.join(SAVE_FOLDER, filename)
    await tg_file.download_to_drive(filepath)
    file_link = f"{BOT_URL}/file/{filename}"
    await update.message.reply_text(f"✅ File saved!\n🔗 Link: {file_link}")

def run_bot():
    app_thread = threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 10000})
    app_thread.start()

    async def start_bot():
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(MessageHandler(filters.ALL, handle_file))
        await app.run_polling()

    asyncio.run(start_bot())

if __name__ == "__main__":
    run_bot()
  

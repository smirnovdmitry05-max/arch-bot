import os
import logging
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_TELEGRAM_ID", "0"))

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

SYSTEM_PROMPT = """Ты — личный ассистент руководителя архитектурного бюро.
Бюро проектирует крупные культурные объекты: храмы, музеи, театры.
Отвечай по-русски. Будь конкретным и кратким."""

history = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start from {update.effective_user.id}, owner is {OWNER_ID}")
    await update.message.reply_text("Привет! Я ваш ассистент архитектурного бюро.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Message from {update.effective_user.id}")
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Доступ закрыт.")
        return
    history.append({"role": "user", "content": update.message.text})
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=history[-10:]
    )
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

if __name__ == "__main__":
    logger.info("Starting bot...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    logger.info("Bot is running!")
    app.run_polling(drop_pending_updates=True)

import os
import requests

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8001")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    message = f"""
Pocket Agenda is ready.

Your chat ID:
{chat_id}

Commands:
/today - Show today's Google Calendar program
/add your event - Add event to Google Calendar
/chat your message - Chat with AI
/yearly your goal - Create yearly plan
/help - Show commands
"""

    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
Commands:

/today
Shows today's Google Calendar events.

/add dentist appointment May 20 2026 at 12 PM remind me 1 hour before
Creates a calendar event with reminder and conflict check.

/chat help me organize my week
Chats with AI.

/yearly 2026 goal: learn Python and prepare for jobs
Creates yearly plan.
"""

    await update.message.reply_text(message)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{BACKEND_URL}/daily-program")
        data = response.json()

        await update.message.reply_text(
            data["message"],
            parse_mode=data.get("parse_mode", None)
        )

    except Exception as error:
        await update.message.reply_text(
            f"Could not get daily program.\nError: {error}"
        )


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)

    if not user_text:
        await update.message.reply_text(
            "Please write an event after /add.\n\nExample:\n/add dentist appointment May 20 2026 at 12 PM remind me 1 hour before"
        )
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/smart-event",
            json={"message": user_text},
        )

        data = response.json()
        await update.message.reply_text(str(data))

    except Exception as error:
        await update.message.reply_text(
            f"Could not add event.\nError: {error}"
        )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)

    if not user_text:
        await update.message.reply_text(
            "Please write a message after /chat.\n\nExample:\n/chat help me organize my week"
        )
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": user_text},
        )

        data = response.json()
        await update.message.reply_text(str(data))

    except Exception as error:
        await update.message.reply_text(
            f"Could not chat with AI.\nError: {error}"
        )


async def yearly_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)

    if not user_text:
        await update.message.reply_text(
            "Please write your yearly goal after /yearly.\n\nExample:\n/yearly 2026 goal: learn Python and prepare for jobs"
        )
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/yearly-plan",
            json={"message": user_text},
        )

        data = response.json()
        await update.message.reply_text(str(data))

    except Exception as error:
        await update.message.reply_text(
            f"Could not create yearly plan.\nError: {error}"
        )


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("add", add_event))
    app.add_handler(CommandHandler("chat", chat))
    app.add_handler(CommandHandler("yearly", yearly_plan))

    print("Telegram bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
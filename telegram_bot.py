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
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    message = (
        "Pocket Agenda is ready.\n\n"
        f"Your chat ID:\n{chat_id}\n\n"
        "Commands:\n"
        "/today - Show today's Google Calendar program\n"
        "/add [your event] - Add event to Google Calendar, then show today's updated schedule\n"
        "/replace [event_id] [new details] - Replace an event\n"
        "/remove [event_id] - Remove an event\n"
        "/chat [your message] - Chat with AI\n"
        "/yearly [your goal] - Create yearly plan\n"
        "/help - Show commands"
    )

    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Commands:\n\n"
        "/today\n"
        "Shows today's Google Calendar events.\n\n"
        "/add dentist appointment May 20 2026 at 12 PM remind me 1 hour before\n"
        "Creates a calendar event with reminder and conflict check, then shows today's updated schedule.\n\n"
        "/replace [event_id] [new details]\n"
        "Replaces an event with new details.\n\n"
        "/remove [event_id]\n"
        "Removes an event from your calendar.\n\n"
        "/chat help me organize my week\n"
        "Chats with AI.\n\n"
        "/yearly 2026 goal: learn Python and prepare for jobs\n"
        "Creates yearly plan."
    )

    await update.message.reply_text(message)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{BACKEND_URL}/daily-program")

        if not response.ok:
            await update.message.reply_text(
                f"Could not get daily program.\n"
                f"Backend error: {response.status_code}\n"
                f"{response.text[:500]}"
            )
            return

        data = response.json()

        message = data["message"]

        if "events" in data and data["events"]:
            message += (
                "\n\nTo replace an event:\n"
                "/replace [event_id] [new details]\n\n"
                "To remove an event:\n"
                "/remove [event_id]"
            )

        await update.message.reply_text(
            message,
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
            "Please write an event after /add.\n\n"
            "Example:\n/add dentist appointment May 20 2026 at 12 PM remind me 1 hour before"
        )
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/smart-event",
            json={"message": user_text},
        )

        if not response.ok:
            await update.message.reply_text(
                f"Could not add event.\n"
                f"Backend error: {response.status_code}\n"
                f"{response.text[:500]}"
            )
            return

        data = response.json()

        if "conflicts" in data:
            message = data.get("message", "Conflict found. Event was not created.")
            message += "\n\nConflicting events:\n"

            for event in data["conflicts"]:
                message += (
                    f"\n- {event['title']}\n"
                    f"  ID: {event['id']}\n"
                    f"  From: {event['start']}\n"
                    f"  To: {event['end']}\n"
                )

            message += (
                "\nTo remove one:\n"
                "/remove [event_id]\n\n"
                "To replace one:\n"
                "/replace [event_id] [new details]"
            )

            await update.message.reply_text(message)
            return

        if "error" in data:
            await update.message.reply_text(
                f"Could not add event.\n{data['error']}"
            )
            return

        message = data.get("message", "Event added.")

        if "event_link" in data and data["event_link"]:
            message += f"\n\nOpen in Google Calendar:\n{data['event_link']}"

        await update.message.reply_text(message)

        today_response = requests.get(f"{BACKEND_URL}/daily-program")

        if today_response.ok:
            today_data = today_response.json()
            await update.message.reply_text(
                today_data["message"],
                parse_mode=today_data.get("parse_mode", None)
            )

    except Exception as error:
        await update.message.reply_text(
            f"Could not add event.\nError: {error}"
        )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)

    if not user_text:
        await update.message.reply_text(
            "Please write a message after /chat.\n\n"
            "Example:\n/chat help me organize my week"
        )
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": user_text},
        )

        if not response.ok:
            await update.message.reply_text(
                f"Could not chat with AI.\n"
                f"Backend error: {response.status_code}\n"
                f"{response.text[:500]}"
            )
            return

        data = response.json()

        if "reply" in data:
            await update.message.reply_text(data["reply"])
        elif "message" in data:
            await update.message.reply_text(data["message"])
        else:
            await update.message.reply_text(str(data))

    except Exception as error:
        await update.message.reply_text(
            f"Could not chat with AI.\nError: {error}"
        )


async def yearly_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)

    if not user_text:
        await update.message.reply_text(
            "Please write your yearly goal after /yearly.\n\n"
            "Example:\n/yearly 2026 goal: learn Python and prepare for jobs"
        )
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/yearly-plan",
            json={"message": user_text},
        )

        if not response.ok:
            await update.message.reply_text(
                f"Could not create yearly plan.\n"
                f"Backend error: {response.status_code}\n"
                f"{response.text[:500]}"
            )
            return

        data = response.json()

        if "message" in data:
            await update.message.reply_text(data["message"])
        elif "plan" in data:
            await update.message.reply_text(data["plan"])
        else:
            await update.message.reply_text(str(data))

    except Exception as error:
        await update.message.reply_text(
            f"Could not create yearly plan.\nError: {error}"
        )


async def replace_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /replace [event_id] [new details]\n"
            "Example: /replace 123 Dentist appointment May 21 2026 at 2 PM"
        )
        return

    event_id = context.args[0]
    new_details = " ".join(context.args[1:])

    try:
        response = requests.post(
            f"{BACKEND_URL}/replace-event",
            json={"event_id": event_id, "new_details": new_details},
        )

        if not response.ok:
            await update.message.reply_text(
                f"Could not replace event.\n"
                f"Backend error: {response.status_code}\n"
                f"{response.text[:500]}"
            )
            return

        data = response.json()
        await update.message.reply_text(str(data))

        today_response = requests.get(f"{BACKEND_URL}/daily-program")

        if today_response.ok:
            today_data = today_response.json()
            await update.message.reply_text(
                today_data["message"],
                parse_mode=today_data.get("parse_mode", None)
            )

    except Exception as error:
        await update.message.reply_text(
            f"Could not replace event.\nError: {error}"
        )


async def remove_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text(
            "Usage: /remove [event_id]\n"
            "Example: /remove 123"
        )
        return

    event_id = context.args[0]

    try:
        response = requests.post(
            f"{BACKEND_URL}/remove-event",
            json={"event_id": event_id},
        )

        if not response.ok:
            await update.message.reply_text(
                f"Could not remove event.\n"
                f"Backend error: {response.status_code}\n"
                f"{response.text[:500]}"
            )
            return

        data = response.json()
        await update.message.reply_text(str(data))

        today_response = requests.get(f"{BACKEND_URL}/daily-program")

        if today_response.ok:
            today_data = today_response.json()
            await update.message.reply_text(
                today_data["message"],
                parse_mode=today_data.get("parse_mode", None)
            )

    except Exception as error:
        await update.message.reply_text(
            f"Could not remove event.\nError: {error}"
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
    app.add_handler(CommandHandler("replace", replace_event))
    app.add_handler(CommandHandler("remove", remove_event))

    print("Telegram bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
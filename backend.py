import os.path
import requests
import random
import json
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi import FastAPI
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
OLLAMA_URL = "http://localhost:11434/api/generate"
TIMEZONE = "America/Toronto"

app = FastAPI()


def get_calendar_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def extract_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return json.loads(text)


@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.get("/daily-program")
def daily():
    service = get_calendar_service()
    now = datetime.now().astimezone()

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    if not events:
        return {
            "message": "📅 <b>Today's schedule</b>\n\n🟩 No events found yet.",
            "events": [],
            "parse_mode": "HTML"
        }

    message = "📅 <b>Today's schedule</b>\n\n"

    for event in events:
        title = event.get("summary", "No title")
        event_id = event.get("id", "")

        start_raw = event["start"].get("dateTime", event["start"].get("date"))
        end_raw = event["end"].get("dateTime", event["end"].get("date"))

        start_dt = datetime.fromisoformat(start_raw)
        end_dt = datetime.fromisoformat(end_raw)

        start_time = start_dt.strftime("%I:%M %p").lstrip("0")
        end_time = end_dt.strftime("%I:%M %p").lstrip("0")

        minutes_until = (start_dt - now).total_seconds() / 60

        if minutes_until <= 60:
            priority_label = "🟥 <b>URGENT</b>"
        elif minutes_until <= 180:
            priority_label = "🟨 <b>NEXT</b>"
        else:
            priority_label = "🟩 <b>LATER</b>"

        message += f"{priority_label}\n"
        message += f"<b>{title}</b> (ID: <code>{event_id}</code>)\n"
        message += f"<u>{start_time} - {end_time}</u>\n\n"

    return {
        "message": message,
        "events": events,
        "parse_mode": "HTML"
    }


@app.post("/chat")
def chat():
    return {
        "reply": "Write a task or event to add your Google Calendar"
    }


class SmartEventRequest(BaseModel):
    message: str


@app.post("/smart-event")
def smart_event(req: SmartEventRequest):
    service = get_calendar_service()
    now = datetime.now().astimezone()
    today = now.date().isoformat()

    prompt = f"""
Extract one Google Calendar event from this text.

Text: {req.message}
Current date: {today}

Return ONLY valid JSON, no explanation, in this exact format:
{{
  "title": "event title",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "reminder_minutes": 60
}}

Rules:
- Use 24-hour time.
- If user says today, use Current date.
- If user says tomorrow, calculate the next date.
- Date must always be YYYY-MM-DD.
- Time must always be HH:MM in 24-hour format.
- If the end time is missing, make the event 1 hour long.
- If reminder is missing, use 60 minutes.
- Return only JSON.
"""

    try:
        ollama_response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
            }
        )
        ollama_response.raise_for_status()
        data = ollama_response.json()
    except Exception as error:
        return {"error": f"Ollama request failed: {error}"}

    ai_answer = data.get("response", "")
    print("OLLAMA ANSWER:", ai_answer)

    try:
        event_info = extract_json(ai_answer)
    except Exception:
        return {
            "error": "Could not parse event details from AI.",
            "ai_answer": ai_answer
        }

    try:
        title = event_info["title"].strip()
        event_date = event_info["date"].strip()
        start_time = event_info["start_time"].strip()
        end_time = event_info["end_time"].strip()
        reminder_minutes = int(event_info.get("reminder_minutes", 60))

        start_dt = datetime.strptime(
            f"{event_date} {start_time}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=now.tzinfo)

        end_dt = datetime.strptime(
            f"{event_date} {end_time}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=now.tzinfo)

    except Exception as error:
        return {
            "error": f"AI returned invalid event details: {error}",
            "event_info": event_info
        }

    if end_dt <= start_dt:
        end_dt = start_dt + timedelta(hours=1)

    start_datetime = start_dt.isoformat()
    end_datetime = end_dt.isoformat()

    try:
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_datetime,
            timeMax=end_datetime,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
    except HttpError as error:
        return {"error": f"Could not check calendar conflicts: {error}"}

    conflicting_events = events_result.get("items", [])

    if conflicting_events:
        conflicts = []

        for conflict_event in conflicting_events:
            conflicts.append({
                "id": conflict_event.get("id"),
                "title": conflict_event.get("summary", "No title"),
                "start": conflict_event["start"].get(
                    "dateTime",
                    conflict_event["start"].get("date")
                ),
                "end": conflict_event["end"].get(
                    "dateTime",
                    conflict_event["end"].get("date")
                ),
            })

        return {
            "error": "Conflict found. Event was not created.",
            "conflicts": conflicts,
            "message": "This event conflicts with an existing event. Use /remove [event_id] or /replace [event_id] [new details]."
        }
    color_id = random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])
    event = {
        "summary": title,
        "colorId": color_id,
        "start": {
            "dateTime": start_datetime,
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": TIMEZONE,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",
                    "minutes": reminder_minutes
                }
            ],
        },
    }

    try:
        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()
    except HttpError as error:
        return {"error": f"Google Calendar could not create event: {error}"}

    return {
        "message": f"Event added: {created_event.get('summary')}",
        "event_id": created_event.get("id"),
        "event_link": created_event.get("htmlLink")
    }


@app.get("/events")
def get_events():
    return {
        "get events": "Get events from Google Calendar"
    }


@app.post("/yearly-plan")
def yearly_plan():
    return {
        "create plan": "Create yearly plan based on users input on chatbot"
    }


class ReplaceEventRequest(BaseModel):
    event_id: str
    new_details: str


class RemoveEventRequest(BaseModel):
    event_id: str


@app.post("/replace-event")
def replace_event(req: ReplaceEventRequest):
    service = get_calendar_service()

    try:
        event = service.events().get(
            calendarId="primary",
            eventId=req.event_id
        ).execute()
    except Exception as error:
        return {"error": f"Event not found: {error}"}

    event["summary"] = req.new_details

    updated_event = service.events().update(
        calendarId="primary",
        eventId=req.event_id,
        body=event
    ).execute()

    return {
        "message": f"Event {req.event_id} replaced.",
        "event": updated_event
    }


@app.post("/remove-event")
def remove_event(req: RemoveEventRequest):
    service = get_calendar_service()

    try:
        service.events().delete(
            calendarId="primary",
            eventId=req.event_id
        ).execute()

        return {"message": f"Event {req.event_id} removed."}

    except Exception as error:
        return {
            "error": f"Event not found or could not be deleted: {error}"
        }
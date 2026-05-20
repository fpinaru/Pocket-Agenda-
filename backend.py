from fastapi import FastAPI
from datetime import datetime 

app = FastAPI()
@app.get("/")
def home():
    return {"message": "Backend is running"}
@app.get("/daily-program")
def daily():
 now = datetime.now().astimezone()
 if not events:
    return { "message": "📅 <b>Today's schedule</b>\n\n🟩 No events found yet.",
        "events": [],
        "parse_mode": "HTML"
    } 
 message = "📅 <b>Today's schedule</b>\n\n"

 for event in events:
    title = event.get("summary", "No title")

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
    message += f"<b>{title}</b>\n"
    message += f"<u>{start_time} - {end_time}</u>\n\n"

 return {
    "message": message,
    "events": events,
    "parse_mode": "HTML"
  }
@app.post("/chat")
def chat():
    return{"reply": "Write a task or event to add your Google Calendar"}
@app.post("/smart-event")
def smart_event():
    return{"analyze chat": "Analyze written chat to create event and its reminder on Google Calendar"}
@app.get("/events")
def events():
    return{"get events": "Get events from Google Calendar"}
@app.post("/yearly-plan")
def yearly_plan():
    return{"create plan": "Create yearly plan based on users input on chatbot"}
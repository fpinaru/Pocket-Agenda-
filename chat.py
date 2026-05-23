import json
import os.path
import requests
import webbrowser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


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


def ask_chatbot(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
        }
    )

    data = response.json()

    if "response" in data:
        return data["response"].strip()

    return f"Error from Ollama: {data}"


def smart_calendar_assistant():
    user_text = input("Tell me what to add to your calendar: ")

    prompt = f"""
Extract one Google Calendar event from this text.

Text: {user_text}

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
- If the end time is missing, make the event 1 hour long.
- If reminder is missing, use 60 minutes.
"""

    ai_answer = ask_chatbot(prompt)

    try:
        event_info = json.loads(ai_answer)
    except json.JSONDecodeError:
        print("I could not understand the event details.")
        print(ai_answer)
        return

    service = get_calendar_service()

    start_datetime = f"{event_info['date']}T{event_info['start_time']}:00"
    end_datetime = f"{event_info['date']}T{event_info['end_time']}:00"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_datetime + "-04:00",
        timeMax=end_datetime + "-04:00",
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    conflicting_events = events_result.get("items", [])

    if conflicting_events:
        print("\nConflict found. This event conflicts with:")

        for event in conflicting_events:
            title = event.get("summary", "No title")
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))

            print(f"- {title}")
            print(f"  From: {start}")
            print(f"  To:   {end}")

        print("\nEvent was NOT created because there is a conflict.")
        return

    event = {
        "summary": event_info["title"],
        "start": {
            "dateTime": start_datetime,
            "timeZone": "America/Toronto",
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": "America/Toronto",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",
                    "minutes": event_info["reminder_minutes"]
                }
            ],
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    event_link = created_event.get("htmlLink")
    print("\nEvent created with reminder!")
    print(event_link)

    webbrowser.open(event_link)


def yearly_calendar_plan():
    year = input("Which year? ")
    goal = input("What is your main goal for this year? ")

    prompt = f"""
Create a yearly calendar plan for {year}.

Main goal: {goal}

Organize the answer by:
- Year
- Months
- Weeks inside each month

For each month, give a main focus.
For each week, give a short plan.
"""

    answer = ask_chatbot(prompt)
    print(answer)

    with open("yearly_calendar_plan.txt", "w", encoding="utf-8") as file:
        file.write(answer)

    print("Saved to yearly_calendar_plan.txt")


while True:
    print("\nCalendar Chatbot App")
    print("1 - Smart calendar assistant")
    print("2 - Chat with AI")
    print("3 - Create yearly calendar plan")
    print("4 - Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        smart_calendar_assistant()

    elif choice == "2":
        prompt = input("Ask me anything: ")
        answer = ask_chatbot(prompt)
        print(answer)

    elif choice == "3":
        yearly_calendar_plan()

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid choice.")
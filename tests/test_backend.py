import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import backend
client = TestClient(backend.app)
#ollama 
def test_home_reports_backend_running():
    response = client.get("/")
    assert response.status_code ==200
    assert response.json() == {"message": "Backend is running"}
@patch("backend.requests.post")
@patch("backend.get_calendar_service")
def test_smart_event_creates_event(mock_calendar, mock_post):
    ollama_answer ={
        "title": "Dentist",
        "date": "2026-05-20",
        "start_time": "12:00",
        "end_time": "13:00",
        "reminder_minutes": 60,

    }
    mock_post.return_value.json.return_value = {"response": json.dumps(ollama_answer)}
    #google-calendar
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {"items": []}
    service.events.return_value.insert.return_value.execute.return_value = {"id": "evt_123", "summary": "Dentist"}
    mock_calendar.return_value = service

    # ACT
   
    response = client.post("/smart-event", json={"message": "dentist May 20 at noon"})
    print("RESPONSE:", response.json())
    # ASSERT
    assert response.json()["event_id"] == "evt_123"
    sent_event = service.events.return_value.insert.call_args.kwargs["body"]
    assert sent_event["summary"] == "Dentist"
    assert sent_event["reminders"]["overrides"][0]["minutes"] == 60
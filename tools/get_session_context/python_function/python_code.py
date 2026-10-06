from ces_public import ces_requests
import urllib.parse
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def get_session_context(session_key: str = 'latest', current_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Combines session, meeting, and weather data using ces_requests.
    current_date: ISO 8601 format or 'Thursday, March 5, 2026'
    """
    base_url = "https://api.openf1.org/v1/"

    # Parsing current_date or using default
    if current_date:
        try:
            # Try simple date format first
            now = datetime.strptime(current_date.split(' (Py')[0], '%A, %B %d, %Y').replace(tzinfo=timezone.utc)
        except:
            try:
                now = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
            except:
                now = datetime(2026, 3, 5, tzinfo=timezone.utc)
    else:
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)

    def fetch(endpoint, params):
        params = {k: v for k, v in params.items() if v is not None}
        query = urllib.parse.urlencode(params)
        url = f"{base_url}{endpoint}?{query}"
        try:
            response = ces_requests.get(url)
            if response.status_code == 200 or (response.status_code == 0 and response.text):
                try:
                    return response.json()
                except:
                    return json.loads(response.text)
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    session_data = fetch("sessions", {"session_key": session_key})

    if isinstance(session_data, dict) and "error" in session_data:
        m2026 = fetch("meetings", {"year": 2026})
        all_meetings = m2026 if isinstance(m2026, list) else []

        started_meetings = []
        for m in all_meetings:
            start_str = m.get("date_start")
            if start_str:
                m_start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                if m_start <= now:
                    started_meetings.append(m)

        if started_meetings:
            started_meetings.sort(key=lambda x: x.get("date_start", ""), reverse=True)
            latest_meeting = started_meetings[0]
            m_key = latest_meeting.get("meeting_key")

            sessions = fetch("sessions", {"meeting_key": m_key})
            if isinstance(sessions, list):
                started_sessions = []
                for s in sessions:
                    s_start = datetime.fromisoformat(s.get("date_start").replace('Z', '+00:00'))
                    if s_start <= now:
                        started_sessions.append(s)
                if started_sessions:
                    session_data = [started_sessions[-1]]
                else:
                    session_data = []
            else:
                session_data = []
        else:
            session_data = []

    if not session_data or not isinstance(session_data, list):
        return {"error": "No recent session found in the timing database. Data may not be available yet for this point in the season."}

    session = session_data[0]
    meeting_key = session.get("meeting_key")
    meeting_data = fetch("meetings", {"meeting_key": meeting_key})
    weather_data = fetch("weather", {"session_key": session.get("session_key")})

    return {
        "status": "historical" if session.get("date_end") and datetime.fromisoformat(session.get("date_end").replace('Z', '+00:00')) < now else "live",
        "session": session,
        "meeting": meeting_data[0] if isinstance(meeting_data, list) and meeting_data else {},
        "current_weather": weather_data[-1] if isinstance(weather_data, list) and weather_data else {}
    }

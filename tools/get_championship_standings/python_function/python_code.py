from ces_public import ces_requests
import urllib.parse
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def get_championship_standings(type: str = 'drivers', year: Optional[int] = None, current_date: Optional[str] = None) -> Any:
    """
    Retrieves current championship standings for drivers / teams.
    type: 'drivers' or 'teams'
    """
    base_url = "https://api.openf1.org/v1/"

    # Parsing current_date or using default
    if current_date:
        try:
            now = datetime.strptime(current_date.split(' (Py')[0], '%A, %B %d, %Y').replace(tzinfo=timezone.utc)
        except:
            try:
                now = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
            except:
                now = datetime(2026, 3, 5, tzinfo=timezone.utc)
    else:
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)

    target_year = year or now.year
    endpoint = "championship_drivers" if type == "drivers" else "championship_teams"

    def fetch(ep, params):
        url = f"{base_url}{ep}?{urllib.parse.urlencode(params)}"
        try:
            response = ces_requests.get(url)
            if response.status_code == 200 or (response.status_code == 0 and response.text):
                try:
                    return response.json()
                except:
                    return json.loads(response.text)
            return []
        except:
            return []

    meetings = fetch("meetings", {"year": target_year})
    if not meetings or not isinstance(meetings, list):
        return {"error": f"No meeting data found for {target_year}"}

    started_meetings = [m for m in meetings if m.get("date_start") and datetime.fromisoformat(m["date_start"].replace('Z', '+00:00')) <= now]
    if not started_meetings:
        return {"error": f"The {target_year} season has not started yet."}

    latest_meeting = max(started_meetings, key=lambda x: x["date_start"])
    m_key = latest_meeting.get("meeting_key")

    standings = fetch(endpoint, {"meeting_key": m_key})
    if not standings or not isinstance(standings, list):
        return {"error": "Standings data currently unavailable for this event."}

    sessions = fetch("sessions", {"meeting_key": m_key})
    if isinstance(sessions, list) and sessions:
        completed_sessions = [s for s in sessions if s.get("date_end") and datetime.fromisoformat(s["date_end"].replace('Z', '+00:00')) <= now]
        if completed_sessions:
            latest_session = max(completed_sessions, key=lambda x: x["date_start"])
            s_key = latest_session.get("session_key")
            current_standings = [s for s in standings if s.get("session_key") == s_key]
            if current_standings:
                return {
                    "year": target_year,
                    "type": type,
                    "as_of": f"{latest_meeting['meeting_name']} - {latest_session['session_name']}",
                    "standings": sorted(current_standings, key=lambda x: x.get("position_current", 999))[:20]
                }

    unique_results = {}
    id_field = "driver_number" if type == "drivers" else "team_name"
    for s in standings:
        key = s.get(id_field)
        if key not in unique_results or s.get("points_current", 0) > unique_results[key].get("points_current", 0):
            unique_results[key] = s

    return {
        "year": target_year,
        "type": type,
        "as_of": latest_meeting.get("meeting_name"),
        "standings": sorted(unique_results.values(), key=lambda x: x.get("position_current", 999))[:20]
    }

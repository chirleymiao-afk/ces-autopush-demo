from ces_public import ces_requests
import urllib.parse
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

def get_driver_season_results(driver_name: str, years: List[int], current_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the final (or current) championship position and points for a driver for seasons from 2023 onwards.
    """
    base_url = "https://api.openf1.org/v1/"
    results = {}

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

    def fetch(endpoint, params):
        params = {k: v for k, v in params.items() if v is not None}
        url = f"{base_url}{endpoint}?{urllib.parse.urlencode(params)}"
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

    for year in years:
        if year < 2023:
            results[year] = "Data only available from 2023 onwards."
            continue

        meetings = fetch("meetings", {"year": year})
        if not meetings or not isinstance(meetings, list):
            results[year] = "No data found"
            continue

        started_meetings = [m for m in meetings if m.get("date_start") and datetime.fromisoformat(m["date_start"].replace('Z', '+00:00')) <= now]

        if not started_meetings:
            results[year] = "Season not yet started"
            continue

        latest_meeting = max(started_meetings, key=lambda x: x["date_start"])
        m_key = latest_meeting.get("meeting_key")

        drivers = fetch("drivers", {"meeting_key": m_key})
        d_num = None
        team = "Unknown"
        if isinstance(drivers, list):
            for d in drivers:
                if driver_name.lower() in d.get("last_name", "").lower() or driver_name.lower() in d.get("full_name", "").lower():
                    d_num = d.get("driver_number")
                    team = d.get("team_name")
                    break

        if d_num is None:
            results[year] = f"Driver not found"
            continue

        standings = fetch("championship_drivers", {"meeting_key": m_key})

        if isinstance(standings, list) and standings:
            driver_entries = [s for s in standings if s.get("driver_number") == d_num]
            if driver_entries:
                best_entry = max(driver_entries, key=lambda x: x.get("points_current", 0))
                results[year] = {
                    "position": best_entry.get("position_current"),
                    "points": best_entry.get("points_current"),
                    "team": team,
                    "status": "Final" if year < now.year else "Current",
                    "as_of_meeting": latest_meeting.get("meeting_name")
                }
            else:
                results[year] = "Standings data unavailable"
        else:
            results[year] = "Standings data unavailable"

    return {"driver": driver_name, "history": results}

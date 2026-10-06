from ces_public import ces_requests
import urllib.parse
import json
from typing import Any, Dict, Optional

def openf1_data_fetcher(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Fetches data from the OpenF1 API using ces_requests.
    Limits the results to the first 50 items.
    """
    base_url = "https://api.openf1.org/v1/"
    url = f"{base_url}{endpoint.lstrip('/')}"

    if params:
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

    try:
        response = ces_requests.get(url)
        if response.status_code == 200 or (response.status_code == 0 and response.text):
            try:
                data = response.json()
            except:
                data = json.loads(response.text)

            if isinstance(data, list):
                if len(data) > 50:
                    return {
                        "warning": f"Large dataset detected ({len(data)} items). Returning first 50 items. Use more specific filters (e.g., driver_number, session_key, year).",
                        "data": data[:50]
                    }
                return data
            return data
        else:
            return {"error": f"HTTP {response.status_code}", "url": url, "text": response.text}
    except Exception as e:
        return {"error": str(e), "url": url}

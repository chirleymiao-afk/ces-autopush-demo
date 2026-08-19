"""Tool to check area-wide network outages for Rogers Communications."""

from typing import Any, Dict


def check_outage(account_number: str) -> Dict[str, Any]:
  """Checks if there is an active area outage affecting the customer's account.

  Args:
      account_number: The 9-digit Rogers account number.

  Returns:
      Dict[str, Any]:
          - has_outage: bool indicating whether an area outage is active.
          - outage_id: Outage incident reference ID if active, else None.
          - estimated_restoration: Estimated time to restore service (ETTR).
  """
  # 1. Deterministic test account routing for simulation / manual testing
  if account_number and str(account_number).endswith("999"):
    return {
        "has_outage": True,
        "outage_id": "ROG-99218",
        "estimated_restoration": "Today, 4:00 PM EST",
    }

  # 2. Check context.variables (App schema or dynamic overrides)
  global_vars = globals()
  context = global_vars.get("context")

  mock_json = None
  if context:
    mock_json = context.variables.get("mock_json")
    if not mock_json:
      mock_json_str = context.variables.get("_session", {}).get("modality")
      if isinstance(mock_json_str, str):
        try:
          import json  # pylint: disable=g-import-not-at-top
          mock_json = json.loads(mock_json_str)
        except Exception:
          mock_json = {}

  if mock_json and "mock_outage" in mock_json:
    return mock_json["mock_outage"]

  # 3. Default deterministic baseline: No active outage on account
  return {
      "has_outage": False,
      "outage_id": None,
      "estimated_restoration": None,
  }

"""Tool to book field technician appointments for Rogers Residential Support."""

from typing import Any, Dict


def book_technician_appointment(account_number: str, time_slot: str) -> Dict[str, Any]:
  """Schedules a field technician dispatch and generates a service ticket.

  Args:
      account_number: The 9-digit Rogers account number.
      time_slot: Preferred appointment window (e.g. 'morning', 'afternoon').

  Returns:
      Dict[str, Any]:
          - ticket_id: Unique Rogers support ticket ID (e.g. 'ROG-88219').
          - appointment_booked: bool indicating successful booking.
          - scheduled_date: Confirmed date for the appointment.
  """
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

  if mock_json and "mock_appointment" in mock_json:
    return mock_json["mock_appointment"]

  return {
      "ticket_id": "ROG-88219",
      "appointment_booked": True,
      "scheduled_date": "Tomorrow, 8:00 AM - 12:00 PM",
  }

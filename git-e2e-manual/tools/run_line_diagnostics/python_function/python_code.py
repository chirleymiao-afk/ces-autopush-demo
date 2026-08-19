"""Tool to perform remote line diagnostics on customer gateway and node."""

from typing import Any, Dict


def run_line_diagnostics(account_number: str) -> Dict[str, Any]:
  """Runs remote DOCSIS/Fiber line diagnostic check on customer gateway.

  Args:
      account_number: The 9-digit Rogers account number.

  Returns:
      Dict[str, Any]:
          - line_status: 'OPTIMAL', 'DEGRADED', or 'OFFLINE'.
          - packet_loss_pct: Percentage of packet loss (0-100).
          - snr_db: Signal-to-noise ratio in decibels.
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

  if mock_json and "mock_line_diagnostics" in mock_json:
    return mock_json["mock_line_diagnostics"]

  return {
      "line_status": "OPTIMAL",
      "packet_loss_pct": 0,
      "snr_db": "38.5 dB",
  }

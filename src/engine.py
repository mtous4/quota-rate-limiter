from typing import Any, Dict, Iterable, List
from src.windows import parse_iso_timestamp, get_minute_window_key, get_hour_window_key, calculate_retry_after
from src.validator import validate_request_tokens, validate_request_key

class ReplayEngine:
    """
    Deterministic replay engine for LLM Gateway Quota and Rate Limiting.
    Implements rules R1 through R8 strictly.
    """

    def __init__(self, limits_config: Dict[str, Any]):
        self.limits_config = limits_config
        self.tiers = limits_config.get("tiers", {})
        self.keys = limits_config.get("keys", {})
        # Minute window request accounting: (key, 'YYYY-MM-DDTHH:mm') -> int
        self.minute_request_counts: Dict[tuple[str, str], int] = {}
        # Hour window token accounting: (key, 'YYYY-MM-DDTHH') -> int
        self.hour_token_counts: Dict[tuple[str, str], int] = {}

    def process_single_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        req_id = req.get("id")

        # Step 1: Pre-accounting validation (Rule R5).
        # Invalid requests consume nothing (neither request slot nor tokens).
        # Check validity before checking the key.
        if not validate_request_tokens(req):
            return {
                "id": req_id,
                "decision": "deny",
                "reason": "invalid_request",
                "retry_after_seconds": None
            }

        # Step 2: Key existence validation (Rule R6).
        # Unknown keys consume nothing.
        if not validate_request_key(req, self.limits_config):
            return {
                "id": req_id,
                "decision": "deny",
                "reason": "unknown_key",
                "retry_after_seconds": None
            }

        key = req["key"]
        tokens = req["tokens"]
        timestamp_str = req["timestamp"]

        # Step 3: Determine wall-clock calendar windows (Rule R1).
        dt = parse_iso_timestamp(timestamp_str)
        minute_key = (key, get_minute_window_key(dt))
        hour_key = (key, get_hour_window_key(dt))

        tier_name = self.keys[key]
        tier_limits = self.tiers[tier_name]
        rpm_limit = tier_limits["requests_per_minute"]
        tph_limit = tier_limits["tokens_per_hour"]

        # Step 4: Evaluate limits (Rule R3).
        # strictly less than requests_per_minute
        current_req_count = self.minute_request_counts.get(minute_key, 0)
        req_ok = (current_req_count < rpm_limit)

        # consumed tokens + this request's tokens <= tokens_per_hour
        current_tok_count = self.hour_token_counts.get(hour_key, 0)
        tok_ok = (current_tok_count + tokens <= tph_limit)

        # Step 5: Accounting (Rule R4).
        # Every request that reaches limit checking (allowed or denied) increments request count.
        self.minute_request_counts[minute_key] = current_req_count + 1

        # Only allowed requests consume tokens.
        if req_ok and tok_ok:
            self.hour_token_counts[hour_key] = current_tok_count + tokens
            return {
                "id": req_id,
                "decision": "allow",
                "reason": None,
                "retry_after_seconds": None
            }
        else:
            # Step 6: Determine denial reason and retry_after_seconds (Rule R7 & R8).
            if (not req_ok) and (not tok_ok):
                reason = "both"
            elif not req_ok:
                reason = "requests_per_minute"
            else:
                reason = "tokens_per_hour"

            retry_after = calculate_retry_after(dt, reason)
            return {
                "id": req_id,
                "decision": "deny",
                "reason": reason,
                "retry_after_seconds": retry_after
            }

    def process_requests(self, requests: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a sequence of requests in exact file order (Rule R2).
        """
        decisions: List[Dict[str, Any]] = []
        for req in requests:
            decisions.append(self.process_single_request(req))
        return decisions

import unittest
from src.engine import ReplayEngine

class TestR5AndR6Validation(unittest.TestCase):
    """
    Protects:
    - Rule R5: Invalid requests are rejected before any accounting.
      - tokens missing, non-integer, or < 1
      - reason: "invalid_request", retry_after_seconds: null
      - consumes nothing (0 slots, 0 tokens)
      - check validity before checking key
    - Rule R6: Unknown keys
      - key absent from limits.json
      - reason: "unknown_key", retry_after_seconds: null
      - consumes nothing (0 slots, 0 tokens)
    """

    def setUp(self):
        self.limits = {
            "tiers": {
                "free": {"requests_per_minute": 2, "tokens_per_hour": 1000}
            },
            "keys": {
                "k1": "free"
            }
        }
        self.engine = ReplayEngine(self.limits)

    def test_invalid_tokens_missing(self):
        """
        Protects: Rule R5.
        Missing tokens field -> invalid_request, retry_after_seconds=null.
        """
        req = {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z"}
        decisions = self.engine.process_requests([req])

        self.assertEqual(decisions[0], {
            "id": "r1",
            "decision": "deny",
            "reason": "invalid_request",
            "retry_after_seconds": None
        })

    def test_invalid_tokens_non_integer(self):
        """
        Protects: Rule R5.
        Floats, strings, booleans, and nulls for tokens are invalid.
        """
        bad_payloads = [
            {"id": "r_float", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 15.5},
            {"id": "r_str", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": "500"},
            {"id": "r_bool", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": True},
            {"id": "r_none", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": None}
        ]

        decisions = self.engine.process_requests(bad_payloads)
        for d in decisions:
            self.assertEqual(d["decision"], "deny")
            self.assertEqual(d["reason"], "invalid_request")
            self.assertIsNone(d["retry_after_seconds"])

    def test_invalid_tokens_less_than_one(self):
        """
        Protects: Rule R5.
        tokens == 0 or negative tokens are invalid.
        """
        bad_payloads = [
            {"id": "r_zero", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 0},
            {"id": "r_neg", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": -10}
        ]

        decisions = self.engine.process_requests(bad_payloads)
        for d in decisions:
            self.assertEqual(d["decision"], "deny")
            self.assertEqual(d["reason"], "invalid_request")
            self.assertIsNone(d["retry_after_seconds"])

    def test_invalid_requests_consume_nothing(self):
        """
        Protects: Rule R5.
        Limit: 2 requests/min.
        Sending 10 invalid requests must NOT consume any request slots.
        Subsequent valid requests must still be allowed.
        """
        requests = [
            {"id": f"r_inv_{i}", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 0}
            for i in range(10)
        ] + [
            {"id": "r_valid_1", "key": "k1", "timestamp": "2026-09-01T10:00:01.000Z", "tokens": 100},
            {"id": "r_valid_2", "key": "k1", "timestamp": "2026-09-01T10:00:02.000Z", "tokens": 100}
        ]

        decisions = self.engine.process_requests(requests)

        for i in range(10):
            self.assertEqual(decisions[i]["reason"], "invalid_request")

        # The 2 valid requests MUST be allowed (quota was not consumed by invalid requests)
        self.assertEqual(decisions[10]["decision"], "allow")
        self.assertEqual(decisions[11]["decision"], "allow")

    def test_invalid_request_checked_before_unknown_key(self):
        """
        Protects: Rule R5 ("Check validity before checking the key").
        If a request has an unknown key AND invalid tokens (e.g. tokens=0),
        reason MUST be "invalid_request", NOT "unknown_key".
        """
        req = {"id": "r_unknown_and_invalid", "key": "non_existent_key", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 0}
        decisions = self.engine.process_requests([req])

        self.assertEqual(decisions[0], {
            "id": "r_unknown_and_invalid",
            "decision": "deny",
            "reason": "invalid_request",
            "retry_after_seconds": None
        })

    def test_unknown_key_consumes_nothing(self):
        """
        Protects: Rule R6.
        An unknown key with valid tokens is denied with "unknown_key", retry_after_seconds=null,
        and consumes nothing.
        """
        requests = [
            {"id": "r_unk", "key": "phantom_key", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 100},
            {"id": "r_valid_1", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 100},
            {"id": "r_valid_2", "key": "k1", "timestamp": "2026-09-01T10:00:01.000Z", "tokens": 100}
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0], {
            "id": "r_unk",
            "decision": "deny",
            "reason": "unknown_key",
            "retry_after_seconds": None
        })

        # k1 quota must be untouched
        self.assertEqual(decisions[1]["decision"], "allow")
        self.assertEqual(decisions[2]["decision"], "allow")

if __name__ == "__main__":
    unittest.main()

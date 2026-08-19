import unittest
from src.engine import ReplayEngine

class TestR4AccountingAsymmetry(unittest.TestCase):
    """
    Protects: Rule R4 — Denials consume a request slot but no tokens.
    - Every request reaching limit checking (allowed or denied) increments the request count for its minute window.
    - Only allowed requests consume tokens.
    """

    def setUp(self):
        self.limits = {
            "tiers": {
                "free": {"requests_per_minute": 3, "tokens_per_hour": 1000}
            },
            "keys": {
                "k1": "free"
            }
        }
        self.engine = ReplayEngine(self.limits)

    def test_token_denial_does_not_consume_tokens(self):
        """
        Protects: Rule R4.
        Key has 1000 tokens/hr.
        Req 1 requests 1500 tokens -> DENIED (tokens_per_hour). Consumes 0 tokens.
        Req 2 requests 800 tokens -> MUST BE ALLOWED because Req 1 consumed no tokens!
        If Req 1 consumed tokens, Req 2 would be incorrectly denied.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 1500},
            {"id": "r2", "key": "k1", "timestamp": "2026-09-01T10:00:01.000Z", "tokens": 800}
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0]["decision"], "deny")
        self.assertEqual(decisions[0]["reason"], "tokens_per_hour")

        self.assertEqual(decisions[1]["decision"], "allow")
        self.assertIsNone(decisions[1]["reason"])

    def test_denial_consumes_request_slot_in_minute_window(self):
        """
        Protects: Rule R4.
        Limit: 3 requests/min, 1000 tokens/hr.
        Req 1: tokens=5000 -> DENIED (tokens_per_hour). (Slots consumed: 1)
        Req 2: tokens=5000 -> DENIED (tokens_per_hour). (Slots consumed: 2)
        Req 3: tokens=5000 -> DENIED (tokens_per_hour). (Slots consumed: 3)
        Req 4: tokens=10   -> DENIED (requests_per_minute)! Even though tokens are fine,
                              the 3 previous denials consumed all 3 request slots.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 5000},
            {"id": "r2", "key": "k1", "timestamp": "2026-09-01T10:00:01.000Z", "tokens": 5000},
            {"id": "r3", "key": "k1", "timestamp": "2026-09-01T10:00:02.000Z", "tokens": 5000},
            {"id": "r4", "key": "k1", "timestamp": "2026-09-01T10:00:03.000Z", "tokens": 10}
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0]["reason"], "tokens_per_hour")
        self.assertEqual(decisions[1]["reason"], "tokens_per_hour")
        self.assertEqual(decisions[2]["reason"], "tokens_per_hour")

        self.assertEqual(decisions[3]["decision"], "deny")
        self.assertEqual(decisions[3]["reason"], "requests_per_minute")

    def test_rpm_denial_further_increments_request_count(self):
        """
        Protects: Rule R4.
        Once RPM is reached, subsequent requests denied for RPM continue incrementing count.
        """
        requests = [
            {"id": f"r{i}", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 10}
            for i in range(1, 6)
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0]["decision"], "allow")
        self.assertEqual(decisions[1]["decision"], "allow")
        self.assertEqual(decisions[2]["decision"], "allow")
        self.assertEqual(decisions[3]["decision"], "deny")
        self.assertEqual(decisions[3]["reason"], "requests_per_minute")
        self.assertEqual(decisions[4]["decision"], "deny")
        self.assertEqual(decisions[4]["reason"], "requests_per_minute")

if __name__ == "__main__":
    unittest.main()

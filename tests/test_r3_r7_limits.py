import unittest
from src.engine import ReplayEngine

class TestR3AndR7Limits(unittest.TestCase):
    """
    Protects: 
    - Rule R3: A request is allowed only if BOTH limits permit it.
    - Rule R7: reason when both limits fail is strictly "both".
    """

    def setUp(self):
        self.limits = {
            "tiers": {
                "free": {"requests_per_minute": 3, "tokens_per_hour": 1000},
                "pro": {"requests_per_minute": 10, "tokens_per_hour": 50000}
            },
            "keys": {
                "k_free": "free",
                "k_pro": "pro"
            }
        }
        self.engine = ReplayEngine(self.limits)

    def test_basic_allowed_request(self):
        """
        Protects: Rule R3 & Output Contract.
        A single request within quota is allowed with null reason and retry_after.
        """
        req = {"id": "r1", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 200}
        decisions = self.engine.process_requests([req])

        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0], {
            "id": "r1",
            "decision": "allow",
            "reason": None,
            "retry_after_seconds": None
        })

    def test_requests_per_minute_exhaustion(self):
        """
        Protects: Rule R3 (strictly less than requests_per_minute).
        Free tier limit = 3 requests/min.
        Requests 1, 2, 3 should be allowed. Request 4 denied with reason "requests_per_minute".
        """
        requests = [
            {"id": f"r{i}", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 50}
            for i in range(1, 5)
        ]
        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0]["decision"], "allow")
        self.assertEqual(decisions[1]["decision"], "allow")
        self.assertEqual(decisions[2]["decision"], "allow")
        self.assertEqual(decisions[3]["decision"], "deny")
        self.assertEqual(decisions[3]["reason"], "requests_per_minute")

    def test_tokens_per_hour_exhaustion_exact_boundary(self):
        """
        Protects: Rule R3 (consumed + request.tokens <= tokens_per_hour).
        Free tier limit = 1000 tokens/hr.
        Req 1 consumes 800 (allowed, remaining 200).
        Req 2 consumes 200 (allowed, reaches exactly 1000).
        Req 3 consumes 1 (denied with tokens_per_hour).
        """
        requests = [
            {"id": "r1", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 800},
            {"id": "r2", "key": "k_free", "timestamp": "2026-09-01T10:00:01.000Z", "tokens": 200},
            {"id": "r3", "key": "k_free", "timestamp": "2026-09-01T10:00:02.000Z", "tokens": 1}
        ]
        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0]["decision"], "allow")
        self.assertEqual(decisions[1]["decision"], "allow")
        self.assertEqual(decisions[2]["decision"], "deny")
        self.assertEqual(decisions[2]["reason"], "tokens_per_hour")

    def test_reason_both_when_both_limits_fail(self):
        """
        Protects: Rule R7.
        Free tier limit = 3 req/min, 1000 tokens/hr.
        3 requests sent consuming 300 tokens each (total 3 reqs, 900 tokens).
        4th request has tokens=200:
        - Request count would be 4th (fails RPM).
        - Tokens would be 900 + 200 = 1100 (fails TPH).
        Reason MUST be "both".
        """
        requests = [
            {"id": "r1", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 300},
            {"id": "r2", "key": "k_free", "timestamp": "2026-09-01T10:00:10.000Z", "tokens": 300},
            {"id": "r3", "key": "k_free", "timestamp": "2026-09-01T10:00:20.000Z", "tokens": 300},
            {"id": "r4", "key": "k_free", "timestamp": "2026-09-01T10:00:30.000Z", "tokens": 200}
        ]
        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[3]["decision"], "deny")
        self.assertEqual(decisions[3]["reason"], "both")

    def test_multiple_keys_independent_quota(self):
        """
        Protects: Key isolation across tiers.
        Key 'k_free' and 'k_pro' have separate buckets and do not interfere.
        """
        requests = [
            {"id": "r1", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 1000},
            {"id": "r2", "key": "k_free", "timestamp": "2026-09-01T10:00:01.000Z", "tokens": 1},  # Denied (TPH)
            {"id": "r3", "key": "k_pro", "timestamp": "2026-09-01T10:00:01.000Z", "tokens": 5000}   # Allowed (Pro tier)
        ]
        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0]["decision"], "allow")
        self.assertEqual(decisions[1]["decision"], "deny")
        self.assertEqual(decisions[2]["decision"], "allow")

if __name__ == "__main__":
    unittest.main()

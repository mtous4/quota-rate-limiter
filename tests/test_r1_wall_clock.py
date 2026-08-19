import unittest
from src.engine import ReplayEngine

class TestR1WallClockWindows(unittest.TestCase):
    """
    Protects: Rule R1 — Windows are aligned to the wall clock, not rolling.
    - Minute window is the calendar UTC minute.
    - Hour window is the calendar UTC hour.
    - Windows do not slide or roll.
    """

    def setUp(self):
        self.limits = {
            "tiers": {
                "free": {"requests_per_minute": 5, "tokens_per_hour": 10000}
            },
            "keys": {
                "k1": "free"
            }
        }
        self.engine = ReplayEngine(self.limits)

    def test_minute_boundary_reset(self):
        """
        Protects: Rule R1 & R3.
        5 requests sent at 10:00:59.900 exhaust the minute quota.
        A 6th request at 10:01:00.100 (200ms later) falls into a NEW calendar minute
        and MUST be allowed.
        """
        requests = [
            {"id": f"r{i}", "key": "k1", "timestamp": "2026-09-01T10:00:59.900Z", "tokens": 100}
            for i in range(1, 6)
        ]
        # 6th request in the new minute window
        requests.append({"id": "r6", "key": "k1", "timestamp": "2026-09-01T10:01:00.100Z", "tokens": 100})

        decisions = self.engine.process_requests(requests)
        
        # First 5 in minute 10:00 are allowed
        for i in range(5):
            self.assertEqual(decisions[i]["decision"], "allow")
            self.assertIsNone(decisions[i]["reason"])
        
        # 6th request is in minute 10:01, so it must be allowed (NOT denied by a rolling 60s window)
        self.assertEqual(decisions[5]["decision"], "allow")
        self.assertIsNone(decisions[5]["reason"])

    def test_hour_boundary_reset(self):
        """
        Protects: Rule R1 & R3.
        Request at 10:59:59.000 exhausts the 10000 token limit.
        Request at 11:00:00.000 falls in the next calendar hour and must be allowed.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:59:59.000Z", "tokens": 10000},
            {"id": "r2", "key": "k1", "timestamp": "2026-09-01T11:00:00.000Z", "tokens": 5000}
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0]["decision"], "allow")
        self.assertEqual(decisions[1]["decision"], "allow")

    def test_no_sliding_lookback(self):
        """
        Protects: Rule R1.
        In a sliding window of 60s, requests between 10:00:30 and 10:01:30 would collide.
        In calendar wall-clock windows, 5 requests at 10:00:50 and 5 requests at 10:01:10
        must BOTH be allowed because they belong to distinct calendar minutes.
        """
        requests = [
            {"id": f"r_min0_{i}", "key": "k1", "timestamp": "2026-09-01T10:00:50.000Z", "tokens": 100}
            for i in range(1, 6)
        ] + [
            {"id": f"r_min1_{i}", "key": "k1", "timestamp": "2026-09-01T10:01:10.000Z", "tokens": 100}
            for i in range(1, 6)
        ]

        decisions = self.engine.process_requests(requests)
        self.assertEqual(len(decisions), 10)
        for d in decisions:
            self.assertEqual(d["decision"], "allow", f"Failed on request {d['id']}")

if __name__ == "__main__":
    unittest.main()

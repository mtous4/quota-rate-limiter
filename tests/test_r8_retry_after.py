import unittest
from src.engine import ReplayEngine

class TestR8RetryAfterCalculation(unittest.TestCase):
    """
    Protects: Rule R8 — retry_after_seconds
    - Number of whole seconds from request timestamp until binding window resets, rounded UP (ceil).
    - Minute denial -> seconds to next calendar minute (:00.000Z).
    - Hour denial -> seconds to next calendar hour (:00:00.000Z).
    - Both denial -> later of the two (hour boundary).
    - Unknown key / invalid request / allow -> null.
    """

    def setUp(self):
        self.limits = {
            "tiers": {
                "free": {"requests_per_minute": 1, "tokens_per_hour": 1000}
            },
            "keys": {
                "k1": "free"
            }
        }
        self.engine = ReplayEngine(self.limits)

    def test_minute_denial_fractional_rounding_up(self):
        """
        Protects: Rule R8.
        Request at 10:00:30.400Z denied on minute limit.
        Next minute starts at 10:01:00.000Z.
        Exact delta = 29.600 seconds.
        Rounded up (ceil) = 30 seconds.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 100}, # Allowed
            {"id": "r2", "key": "k1", "timestamp": "2026-09-01T10:00:30.400Z", "tokens": 100}  # Denied (RPM)
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[1]["decision"], "deny")
        self.assertEqual(decisions[1]["reason"], "requests_per_minute")
        self.assertEqual(decisions[1]["retry_after_seconds"], 30)

    def test_minute_denial_near_boundary(self):
        """
        Protects: Rule R8.
        Request at 10:00:59.999Z denied on minute limit.
        Delta = 0.001 seconds.
        Rounded up (ceil) = 1 second.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 100},
            {"id": "r2", "key": "k1", "timestamp": "2026-09-01T10:00:59.999Z", "tokens": 100}
        ]

        decisions = self.engine.process_requests(requests)
        self.assertEqual(decisions[1]["retry_after_seconds"], 1)

    def test_minute_denial_exact_second_boundary(self):
        """
        Protects: Rule R8.
        Request at 10:00:30.000Z denied on minute limit.
        Delta = 30.000 seconds.
        Rounded up (ceil) = 30 seconds.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 100},
            {"id": "r2", "key": "k1", "timestamp": "2026-09-01T10:00:30.000Z", "tokens": 100}
        ]

        decisions = self.engine.process_requests(requests)
        self.assertEqual(decisions[1]["retry_after_seconds"], 30)

    def test_hour_denial_retry_after(self):
        """
        Protects: Rule R8.
        Request at 10:15:30.500Z denied on token limit (1000 tokens/hr).
        Reset is at 11:00:00.000Z (44 minutes, 29.5 seconds = 2669.5 seconds).
        Rounded up (ceil) = 2670 seconds.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:15:30.500Z", "tokens": 5000}
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[0]["decision"], "deny")
        self.assertEqual(decisions[0]["reason"], "tokens_per_hour")
        self.assertEqual(decisions[0]["retry_after_seconds"], 2670)

    def test_both_denial_takes_later_boundary(self):
        """
        Protects: Rule R8 ("Denied on 'both' -> the later of the two, i.e. the hour boundary").
        Request at 10:45:00.000Z fails both RPM and TPH.
        Hour reset is at 11:00:00.000Z (15 minutes = 900 seconds).
        Minute reset would be 60 seconds.
        Must use the later boundary (hour): 900 seconds.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:45:00.000Z", "tokens": 1000}, # Allowed, uses all 1000 tokens & 1 request slot
            {"id": "r2", "key": "k1", "timestamp": "2026-09-01T10:45:10.000Z", "tokens": 500}   # Denied (both)
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(decisions[1]["decision"], "deny")
        self.assertEqual(decisions[1]["reason"], "both")
        # 10:45:10.000Z to 11:00:00.000Z = 14 minutes, 50 seconds = 890 seconds
        self.assertEqual(decisions[1]["retry_after_seconds"], 890)

if __name__ == "__main__":
    unittest.main()

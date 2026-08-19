import unittest
import tempfile
import os
import json
from src.engine import ReplayEngine
from src.cli import run_replay

class TestEdgeCases(unittest.TestCase):
    """
    Additional edge cases and stress tests protecting rules R1 through R8.
    """

    def setUp(self):
        self.limits = {
            "tiers": {
                "free": {"requests_per_minute": 2, "tokens_per_hour": 1000},
                "enterprise": {"requests_per_minute": 1000, "tokens_per_hour": 10000000}
            },
            "keys": {
                "k_free": "free",
                "k_ent": "enterprise"
            }
        }
        self.engine = ReplayEngine(self.limits)

    def test_empty_requests_file(self):
        """
        Protects: Output contract on empty input.
        An empty requests.jsonl should produce an empty decisions.jsonl.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = os.path.join(tmpdir, "empty_req.jsonl")
            lim_path = os.path.join(tmpdir, "limits.json")
            dec_path = os.path.join(tmpdir, "empty_dec.jsonl")

            with open(req_path, "w", encoding="utf-8") as f:
                pass
            with open(lim_path, "w", encoding="utf-8") as f:
                json.dump(self.limits, f)

            run_replay(req_path, lim_path, dec_path)

            self.assertTrue(os.path.exists(dec_path))
            with open(dec_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 0)

    def test_exact_hour_boundary_retry_seconds(self):
        """
        Protects: Rule R8 exact boundary math.
        A request at exactly 10:00:00.000Z denied on tokens_per_hour.
        Next hour begins at 11:00:00.000Z (exactly 3600 seconds).
        retry_after_seconds MUST be 3600.
        """
        requests = [
            {"id": "r_boundary", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 5000}
        ]
        decisions = self.engine.process_requests(requests)
        self.assertEqual(decisions[0]["decision"], "deny")
        self.assertEqual(decisions[0]["reason"], "tokens_per_hour")
        self.assertEqual(decisions[0]["retry_after_seconds"], 3600)

    def test_single_request_exceeding_total_capacity(self):
        """
        Protects: Rule R3 & R4.
        A single request with tokens=9999999 on a tier with 1000 limit.
        Must be denied with tokens_per_hour, consumes 1 request slot, and 0 tokens.
        """
        requests = [
            {"id": "r_huge", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 9999999},
            {"id": "r_normal", "key": "k_free", "timestamp": "2026-09-01T10:00:01.000Z", "tokens": 500}
        ]
        decisions = self.engine.process_requests(requests)
        self.assertEqual(decisions[0]["decision"], "deny")
        self.assertEqual(decisions[0]["reason"], "tokens_per_hour")
        # r_normal must be allowed because r_huge consumed 0 tokens
        self.assertEqual(decisions[1]["decision"], "allow")

    def test_midnight_and_month_rollover(self):
        """
        Protects: Rule R1 (wall-clock calendar alignment across midnight/months).
        Request 1 at 2026-09-30T23:59:59.999Z (Sep 30, 23:59)
        Request 2 at 2026-10-01T00:00:00.001Z (Oct 01, 00:00)
        Belongs to distinct minute and hour windows.
        """
        requests = [
            {"id": "r_sep", "key": "k_free", "timestamp": "2026-09-30T23:59:59.999Z", "tokens": 1000},
            {"id": "r_oct", "key": "k_free", "timestamp": "2026-10-01T00:00:00.001Z", "tokens": 1000}
        ]
        decisions = self.engine.process_requests(requests)
        self.assertEqual(decisions[0]["decision"], "allow")
        self.assertEqual(decisions[1]["decision"], "allow")

    def test_strict_boolean_token_rejection(self):
        """
        Protects: Rule R5 (in Python, isinstance(True, int) is True, but booleans are invalid tokens).
        """
        requests = [
            {"id": "r_bool_true", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": True},
            {"id": "r_bool_false", "key": "k_free", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": False}
        ]
        decisions = self.engine.process_requests(requests)
        self.assertEqual(decisions[0]["reason"], "invalid_request")
        self.assertEqual(decisions[1]["reason"], "invalid_request")

if __name__ == "__main__":
    unittest.main()

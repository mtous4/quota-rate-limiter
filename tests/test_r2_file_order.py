import unittest
from src.engine import ReplayEngine

class TestR2FileOrderProcessing(unittest.TestCase):
    """
    Protects: Rule R2 — Process in file order. Do not sort.
    - Input file is not guaranteed to be in timestamp order.
    - Engine must process requests in line order without sorting.
    - Decisions must be returned in the exact same order as input.
    """

    def setUp(self):
        self.limits = {
            "tiers": {
                "free": {"requests_per_minute": 2, "tokens_per_hour": 10000}
            },
            "keys": {
                "k1": "free"
            }
        }
        self.engine = ReplayEngine(self.limits)

    def test_out_of_order_timestamps_preserve_file_order_evaluation(self):
        """
        Protects: Rule R2 & R4.
        Input file has:
        1. r1 at 10:00:50 (tokens: 500)
        2. r2 at 10:00:10 (tokens: 500)
        3. r3 at 10:00:05 (tokens: 500) -> Should be DENIED because r1 and r2 already filled the 2-request limit!
        If sorted by timestamp, r3 (10:00:05) would be processed first and allowed, which is WRONG.
        """
        requests = [
            {"id": "r1", "key": "k1", "timestamp": "2026-09-01T10:00:50.000Z", "tokens": 500},
            {"id": "r2", "key": "k1", "timestamp": "2026-09-01T10:00:10.000Z", "tokens": 500},
            {"id": "r3", "key": "k1", "timestamp": "2026-09-01T10:00:05.000Z", "tokens": 500}
        ]

        decisions = self.engine.process_requests(requests)

        self.assertEqual(len(decisions), 3)
        self.assertEqual(decisions[0]["id"], "r1")
        self.assertEqual(decisions[0]["decision"], "allow")

        self.assertEqual(decisions[1]["id"], "r2")
        self.assertEqual(decisions[1]["decision"], "allow")

        self.assertEqual(decisions[2]["id"], "r3")
        self.assertEqual(decisions[2]["decision"], "deny")
        self.assertEqual(decisions[2]["reason"], "requests_per_minute")

    def test_output_order_strictly_matches_input_order(self):
        """
        Protects: Rule R2 & Output Contract.
        The output lines must match the exact input IDs and sequence.
        """
        requests = [
            {"id": "r_zebra", "key": "k1", "timestamp": "2026-09-01T10:05:00.000Z", "tokens": 100},
            {"id": "r_alpha", "key": "k1", "timestamp": "2026-09-01T10:01:00.000Z", "tokens": 100},
            {"id": "r_beta", "key": "k1", "timestamp": "2026-09-01T10:03:00.000Z", "tokens": 100}
        ]

        decisions = self.engine.process_requests(requests)
        output_ids = [d["id"] for d in decisions]
        self.assertEqual(output_ids, ["r_zebra", "r_alpha", "r_beta"])

if __name__ == "__main__":
    unittest.main()

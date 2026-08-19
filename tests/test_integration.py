import unittest
import json
import tempfile
import os
from src.cli import run_replay

class TestReplayIntegration(unittest.TestCase):
    """
    Protects: End-to-end integration, single-command invocation, determinism,
    and exact output formatting contracts.
    """

    def setUp(self):
        self.limits_data = {
            "tiers": {
                "free": {"requests_per_minute": 2, "tokens_per_hour": 1000},
                "pro": {"requests_per_minute": 5, "tokens_per_hour": 10000}
            },
            "keys": {
                "k1": "free",
                "k2": "pro"
            }
        }
        self.requests_lines = [
            {"id": "r001", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 500},
            {"id": "r002", "key": "k1", "timestamp": "2026-09-01T10:00:10.000Z", "tokens": 400},
            {"id": "r003", "key": "k1", "timestamp": "2026-09-01T10:00:20.000Z", "tokens": 200}, # Denied (both or RPM depending on token cost)
            {"id": "r004", "key": "k_unknown", "timestamp": "2026-09-01T10:00:25.000Z", "tokens": 100},
            {"id": "r005", "key": "k2", "timestamp": "2026-09-01T10:00:30.000Z", "tokens": 2000}
        ]

    def test_end_to_end_replay_file_contract(self):
        """
        Tests the file-in -> file-out CLI execution.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            limits_path = os.path.join(tmpdir, "limits.json")
            requests_path = os.path.join(tmpdir, "requests.jsonl")
            decisions_path = os.path.join(tmpdir, "decisions.jsonl")

            with open(limits_path, "w", encoding="utf-8") as f:
                json.dump(self.limits_data, f)

            with open(requests_path, "w", encoding="utf-8") as f:
                for line in self.requests_lines:
                    f.write(json.dumps(line) + "\n")

            # Execute replay CLI entrypoint
            run_replay(requests_path, limits_path, decisions_path)

            self.assertTrue(os.path.exists(decisions_path))
            with open(decisions_path, "r", encoding="utf-8") as f:
                output_lines = [json.loads(line) for line in f if line.strip()]

            self.assertEqual(len(output_lines), 5)
            self.assertEqual(output_lines[0]["id"], "r001")
            self.assertEqual(output_lines[0]["decision"], "allow")

            self.assertEqual(output_lines[1]["id"], "r002")
            self.assertEqual(output_lines[1]["decision"], "allow")

            self.assertEqual(output_lines[2]["id"], "r003")
            self.assertEqual(output_lines[2]["decision"], "deny")

            self.assertEqual(output_lines[3]["id"], "r004")
            self.assertEqual(output_lines[3]["decision"], "deny")
            self.assertEqual(output_lines[3]["reason"], "unknown_key")

            self.assertEqual(output_lines[4]["id"], "r005")
            self.assertEqual(output_lines[4]["decision"], "allow")

    def test_replay_determinism(self):
        """
        Protects: Determinism requirement. Same input must produce identical output across multiple runs.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            limits_path = os.path.join(tmpdir, "limits.json")
            requests_path = os.path.join(tmpdir, "requests.jsonl")
            decisions_1 = os.path.join(tmpdir, "decisions_1.jsonl")
            decisions_2 = os.path.join(tmpdir, "decisions_2.jsonl")

            with open(limits_path, "w", encoding="utf-8") as f:
                json.dump(self.limits_data, f)

            with open(requests_path, "w", encoding="utf-8") as f:
                for line in self.requests_lines:
                    f.write(json.dumps(line) + "\n")

            run_replay(requests_path, limits_path, decisions_1)
            run_replay(requests_path, limits_path, decisions_2)

            with open(decisions_1, "r", encoding="utf-8") as f1, open(decisions_2, "r", encoding="utf-8") as f2:
                self.assertEqual(f1.read(), f2.read())

if __name__ == "__main__":
    unittest.main()

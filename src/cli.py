import sys
import json
import os
from src.engine import ReplayEngine

def run_replay(requests_file_path: str, limits_file_path: str, decisions_file_path: str) -> None:
    """
    Executes the deterministic replay process:
    Reads limits.json and requests.jsonl, computes decisions in file order,
    and writes decisions.jsonl.
    """
    if not os.path.exists(limits_file_path):
        raise FileNotFoundError(f"Limits file not found: {limits_file_path}")
    if not os.path.exists(requests_file_path):
        raise FileNotFoundError(f"Requests file not found: {requests_file_path}")

    with open(limits_file_path, "r", encoding="utf-8") as f:
        limits_config = json.load(f)

    engine = ReplayEngine(limits_config)

    with open(requests_file_path, "r", encoding="utf-8") as in_f, \
         open(decisions_file_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            line_str = line.strip()
            if not line_str:
                continue
            req = json.loads(line_str)
            decision = engine.process_single_request(req)
            out_f.write(json.dumps(decision) + "\n")

def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python -m src.cli <requests.jsonl> <limits.json> <decisions.jsonl>", file=sys.stderr)
        sys.exit(1)

    requests_path = sys.argv[1]
    limits_path = sys.argv[2]
    decisions_path = sys.argv[3]

    run_replay(requests_path, limits_path, decisions_path)

if __name__ == "__main__":
    main()

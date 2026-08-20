# Quota & Rate Limiting Service (Replay Engine)

A deterministic, offline replay engine that evaluates historical API request logs for an LLM Gateway against tier-based rate and token quota limits.

---

## 1. Project Purpose

An LLM gateway sits in front of a paid model API. Every incoming request consumes both a **request slot** and a **token allowance**. This service processes historical requests sequentially and outputs access decisions (`allow` or `deny`), accompanied by denial reasons and retry-after durations.

Key architectural properties:
- **Replay Engine, Not a Live Server**: Evaluates static files in batch; does not run an HTTP daemon or network listener.
- **Strictly Deterministic**: Identical input files produce byte-for-byte identical output files on every execution.
- **Zero External Infrastructure**: No databases, caches, or network calls.

---

## 2. Input and Output Specifications

### Inputs

1. **`requests.jsonl`** — One JSON object per line:
   ```json
   {"id": "r001", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 1500}
   ```
   - `id` (`string`): Unique request identifier.
   - `key` (`string`): API key used for authentication and quota allocation.
   - `timestamp` (`string`): UTC timestamp formatted strictly as ISO 8601 with millisecond precision and a trailing `Z`.
   - `tokens` (`integer`): Declared token cost of the request.

2. **`limits.json`** — JSON configuration for tiers and key mappings:
   ```json
   {
     "tiers": {
       "free": { "requests_per_minute": 5, "tokens_per_hour": 10000 },
       "pro":  { "requests_per_minute": 60, "tokens_per_hour": 500000 }
     },
     "keys": {
       "k1": "free",
       "k2": "pro"
     }
   }
   ```

### Output

**`decisions.jsonl`** — Exactly one JSON object per input request, written in the identical order as `requests.jsonl`:
```json
{"id": "r001", "decision": "allow", "reason": null, "retry_after_seconds": null}
{"id": "r007", "decision": "deny", "reason": "requests_per_minute", "retry_after_seconds": 23}
```
- `id` (`string`): Matches input request `id`.
- `decision` (`string`): Exactly `"allow"` or `"deny"`.
- `reason` (`string` | `null`): `null` when allowed. When denied, exactly one of:
  - `"requests_per_minute"` — Per-minute request slot limit exceeded.
  - `"tokens_per_hour"` — Per-hour token allowance exceeded.
  - `"both"` — Both limits exceeded simultaneously.
  - `"unknown_key"` — `key` not found in `limits.json`.
  - `"invalid_request"` — Malformed `tokens` field (missing, non-integer, or $<1$).
- `retry_after_seconds` (`integer` | `null`): Integer seconds until the binding reset boundary, rounded **up** (ceiling). `null` when allowed, unknown key, or invalid request.

---

## 3. High-Level System Rules & Mechanics

The engine strictly implements rules R1 through R8 from the specification:
- **R1 (Wall-Clock Windows)**: Minute and hour windows are aligned to calendar UTC (`:00.000` to `:59.999`). Windows do not slide; there is no rolling lookback.
- **R2 (File Order Processing)**: Requests are processed strictly in physical file order without timestamp sorting.
- **R3 (Dual Limit Conjunction)**: A request is allowed iff `counted_requests < requests_per_minute` (strict `<`) **and** `consumed_tokens + tokens <= tokens_per_hour` (inclusive `<=`).
- **R4 (Asymmetric Denial Accounting)**: Every evaluated request (allowed or denied) consumes 1 request slot. Only allowed requests consume tokens.
- **R5 (Pre-Accounting Validation)**: Invalid `tokens` are rejected as `"invalid_request"` with 0 quota consumption. Evaluated *before* key lookup.
- **R6 (Unknown Keys)**: Keys missing from `limits.json` are rejected as `"unknown_key"` with 0 quota consumption.
- **R7 (Dual Limit Reason)**: When both RPM and TPH limits fail simultaneously, `reason` is `"both"`.
- **R8 (Ceiling Retry Delta)**: `retry_after_seconds` is the whole number of seconds from the request timestamp until the next window reset, rounded **up** ($\lceil \Delta t / 1000 \rceil$).

---

## 4. Requirements & Setup

- **Python Version**: Python 3.10+ (tested on Python 3.12.4).
- **Dependencies**: **Zero external dependencies** (Pure Python Standard Library: `json`, `datetime`, `math`, `os`, `sys`, `unittest`, `typing`).

### Setup Steps
1. Clone repository:
   ```bash
   git clone <repository_url>
   cd quota-rate-limiter
   ```
2. No installation or virtual environment is required.

---

## 5. Execution Commands

### Run the Replay Engine
```bash
python -m src.cli requests.jsonl limits.json decisions.jsonl
```
*(Or specify custom file paths: `python -m src.cli path/to/requests.jsonl path/to/limits.json path/to/decisions.jsonl`)*
![alt text](image-1.png)

### Run the Test Suite
```bash
python -m unittest discover -s tests -v
```
![alt text](image.png) 

---

## 6. Project Structure

```text
quota-rate-limiter/
├── BRIEF.md                 # Complete problem specification
├── EVIDENCE.md              # Test verification evidence & reproduction claims
├── README.md                # Clean-clone execution guide
├── limits.json              # Sample limits configuration
├── requests.jsonl           # Sample requests log
├── image.png                # Verification screenshot
├── image-1.png              # Execution output screenshot
├── image-2.png              # Screenshot
├── image-3.png              # Screenshot
├── image-4.png              # Screenshot
├── image-5.png              # Screenshot
├── image-6.png              # Screenshot
├── image-7.png              # Screenshot
├── image-8.png              # Screenshot
├── src/                     # Deliverable 3: Replay engine implementation
│   ├── __init__.py
│   ├── cli.py               # Single command CLI entrypoint
│   ├── engine.py            # Sequential replay engine & quota state manager
│   ├── validator.py         # Request validation & key existence checks (R5, R6)
│   └── windows.py           # Wall-clock UTC bucket derivation & ceiling retry math (R1, R8)
└── tests/                   # Deliverable 2: Automated test suite
    ├── fixtures/
    │   └── limits.json
    ├── test_r1_wall_clock.py
    ├── test_r2_file_order.py
    ├── test_r3_r7_limits.py
    ├── test_r4_accounting.py
    ├── test_r5_r6_validation.py
    ├── test_r8_retry_after.py
    ├── test_edge_cases.py
    └── test_integration.py
```

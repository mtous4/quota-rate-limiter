# Project 1 — Quota & Rate Limiting Service

**One week. Graded out of 10 against `RUBRIC_final_projects.md` — read that first.**

This is the **fully specified** project. Everything you need to know about correct behaviour is in this document. There is no ambiguity to resolve and no stakeholder to interview. That is deliberate: the only variables being measured this week are whether you verified your work, whether your report is honest, and whether you can defend it.

I hold an acceptance test suite you will not see, run against data you do not have. It tests the spec below, exactly as written.

---

## The problem

An LLM gateway sits in front of a paid model API. Every incoming request consumes both a **request slot** and a **token allowance**. Your job is a service that decides, for each request, whether it is allowed or denied — and if denied, when the caller may retry.

You are building a **replay engine**, not a live server. It reads a file of requests, decides each one in order, and writes a file of decisions. Same input, same output, every time.

---

## Inputs

### `requests.jsonl` — one JSON object per line

```json
{"id": "r001", "key": "k1", "timestamp": "2026-09-01T10:00:00.000Z", "tokens": 1500}
```

- `id` — unique string
- `key` — API key
- `timestamp` — UTC, ISO 8601, always with milliseconds and a trailing `Z`
- `tokens` — integer, the token cost of the request

### `limits.json`

```json
{
  "tiers": {
    "free":  { "requests_per_minute": 5,  "tokens_per_hour": 10000 },
    "pro":   { "requests_per_minute": 60, "tokens_per_hour": 500000 }
  },
  "keys": { "k1": "free", "k2": "pro" }
}
```

---

## Output

### `decisions.jsonl` — exactly one line per input request, in the same order as the input file

```json
{"id": "r001", "decision": "allow", "reason": null, "retry_after_seconds": null}
{"id": "r007", "decision": "deny", "reason": "requests_per_minute", "retry_after_seconds": 23}
```

- `decision` — `"allow"` or `"deny"`
- `reason` — `null` when allowed. When denied, exactly one of: `"requests_per_minute"`, `"tokens_per_hour"`, `"both"`, `"unknown_key"`, `"invalid_request"`
- `retry_after_seconds` — integer when denied by a limit, otherwise `null`

---

## Rules

Read these carefully. Several of them are **not** how rate limiters are usually built.

### R1 — Windows are aligned to the wall clock, not rolling

The minute window is the calendar UTC minute. The hour window is the calendar UTC hour.

A request at `10:00:59.900` and a request at `10:01:00.100` fall in **different minute windows**, 200 ms apart. A request at `10:59:59.000` and one at `11:00:00.000` fall in different hour windows.

Windows do not slide. There is no rolling lookback.

### R2 — Process in file order. Do not sort.

The input file is **not guaranteed to be in timestamp order**. Process the requests in the order they appear in the file. Each request is assigned to its windows using its own timestamp.

Do not sort the input. Sorting produces different output, and the acceptance tests will catch it.

### R3 — A request is allowed only if both limits permit it

At the moment a request is processed, it is allowed only if **both** hold:

- the number of requests already **counted** against that key in this request's minute window is **strictly less than** `requests_per_minute`; and
- tokens already **consumed** by that key in this request's hour window, **plus this request's `tokens`**, is **less than or equal to** `tokens_per_hour`.

### R4 — Denials consume a request slot but no tokens

This is the rule most implementations get wrong.

- Every request that reaches limit checking — **allowed or denied** — increments the request count for its minute window.
- **Only allowed requests consume tokens.**

A denied request therefore costs the caller quota on one axis and not the other.

### R5 — Invalid requests are rejected before any accounting

A request is invalid if `tokens` is missing, not an integer, or less than 1.

Invalid requests are denied with reason `"invalid_request"`, `retry_after_seconds: null`, and **they consume nothing** — neither a request slot nor tokens. They are not counted in any window.

Check validity before checking the key.

### R6 — Unknown keys

A `key` absent from `limits.json` is denied with reason `"unknown_key"` and `retry_after_seconds: null`. It consumes nothing.

### R7 — `reason` when both limits fail

If the request would be denied by the per-minute limit **and** the per-hour token limit, `reason` is `"both"`.

### R8 — `retry_after_seconds`

The number of whole seconds from **this request's timestamp** until the binding window next resets, **rounded up**.

- Denied on `requests_per_minute` → seconds until the next calendar minute begins.
- Denied on `tokens_per_hour` → seconds until the next calendar hour begins.
- Denied on `"both"` → the **later** of the two, i.e. the hour boundary.

Rounded up means a request at `10:00:30.400` denied on the minute limit gets `30`, not `29`. Work out why before you write the code.

---

## What you deliver

The six deliverables from the rubric, in that order:

1. `UNDERSTANDING.md` — this problem in your own words. Since the spec is complete, what I am looking for here is **which rules you identified as unusual**, and what you expect the consequence of each to be. Write it before you write code.
2. **Your own test suite**, written before the implementation.
3. The implementation. A single command must turn `requests.jsonl` + `limits.json` into `decisions.jsonl`.
4. `EVIDENCE.md` — what you tested, what counts as correct, and the command that regenerates every claim.
5. `AI_LOG.md` — what you delegated, what came back, how you verified it.
6. `QUESTIONS.md` — every question you asked, and what changed as a result.

Plus a `README.md` whose commands run on a clean clone. I will clone it fresh and follow it exactly.

---

## Hard rules

1. **No implementation code committed before `UNDERSTANDING.md`.** The rubric caps that axis at 1 if it happens.
2. Determinism: same inputs, same outputs, every run.
3. No network calls. No database. Files in, files out.
4. Every number in `EVIDENCE.md` must come from a command you can run in front of me.
5. Commit as you go. I will read the history.

---

## How this will be graded

Against the five axes in the rubric. Specifically for this project:

- **Working code** — your output compared line by line against expected output on inputs you have not seen.
- **Problem understanding** — did you spot the rules that differ from the standard approach, before building?
- **Verification** — do your own tests cover the unusual rules, or only the obvious path?
- **Honest reporting** — does `EVIDENCE.md` tell me what you did not manage to handle?
- **Defence** — can you explain any line I point at, including the ones the AI wrote?

---

## One piece of advice

Use AntiGravity. Let it write the code. But notice that if you paste this brief into it and accept what comes back, you will get a textbook rate limiter with rolling windows, sorted input, and denials that cost nothing — and it will fail on rules R1, R2, R4 and R8.

The gap between that and a passing implementation is you having read the spec. That gap is the entire project.

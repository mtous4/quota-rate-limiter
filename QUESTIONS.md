# Project Questions & Decision Log

## "This file made by Ai based on questions i asked"

## 1. Overview & Project Context

As stated in `BRIEF.md`:
> *"This is the fully specified project. Everything you need to know about correct behaviour is in this document. There is no ambiguity to resolve and no stakeholder to interview."*

Because the behavioral specification was complete from the start, no questions were required to resolve missing business logic. However, several critical technical, workflow, and tooling questions arose during development and verification. Every question asked during the project is factually documented below.

---

## 2. Record of Questions Asked & Resolutions

### Question 1: Workflow Sequencing & Identifying Non-Standard Rules
* **Question**: How should the project be phased to satisfy the rubric, and what are the critical rule deviations from standard rate limiters?
* **Relevant Context / Rule**: `BRIEF.md` Rules R1, R2, R4, R8, and `RUBRIC_final_projects.md` (Hard caps on Deliverable order).
* **Resolution**: Identified that standard rate limiters (rolling windows, sorting timestamps, zero-cost denials) would fail hidden tests. Identified the 4 core traps:
  1. R1: Fixed calendar UTC windows, strictly no rolling lookback.
  2. R2: File order processing without sorting.
  3. R4: Denials actively consume a request slot (but 0 tokens).
  4. R8: Ceiling math ($\lceil \Delta t / 1000 \rceil$) for retry calculation.
* **What Changed as a Result**: Established a strict Test-Driven Development (TDD) sequence: `UNDERSTANDING.md` $\rightarrow$ Test Suite $\rightarrow$ Implementation $\rightarrow$ `EVIDENCE.md` $\rightarrow$ `AI_LOG.md` $\rightarrow$ `QUESTIONS.md` $\rightarrow$ `README.md`.

---

### Question 2: Git Commit Cadence & User Review Policy
* **Question**: How should Git commits be managed during pair programming?
* **Relevant Context**: User directive: *"do not do any commit on github without my acceptance... get them back as changes so I can review them"*.
* **Resolution**: Reset the repository back to the original initial commit (`69667a7`) using a mixed reset, keeping all written files (`UNDERSTANDING.md`, `tests/`, `src/`, `EVIDENCE.md`, etc.) in the working tree.
* **What Changed as a Result**: AI ceased making automatic commits. All files remain in the working tree for explicit review and manual approval by the user.

---

### Question 3: Source Control Visibility & Editor Buffer Synchronization
* **Question**: Why were edits to `UNDERSTANDING.md` and `AI_LOG.md` not appearing in the IDE Source Control tab?
* **Relevant Context**: Local file system state vs. IDE editor memory buffers.
* **Resolution**: Clarified that edits in editor tabs must be saved to disk (`Ctrl + S`) before Git can detect changes from `0 bytes`, and the project directory must be opened as the active workspace folder.
* **What Changed as a Result**: Files were saved to disk, ensuring accurate file sizes and active Git status tracking.

---

### Question 4: Purpose & Timing of `EVIDENCE.md`
* **Question**: What is `EVIDENCE.md` and why was it initially empty?
* **Relevant Context**: `RUBRIC_final_projects.md` (Deliverable #4 & Honest Reporting axis).
* **Resolution**: Explained that `EVIDENCE.md` is the proof artifact containing verifiable test outputs, pass rates, and reproduction commands. It must remain empty until the implementation is built and verified to prevent unverified or fabricated claims.
* **What Changed as a Result**: After implementation, `EVIDENCE.md` was populated with the results of 31 test cases across 8 test modules and reproduction CLI commands.

---

### Question 5: Specification Adherence & Edge-Case Completeness
* **Question**: Is the implementation fully compliant with `BRIEF.md`, and are there subtle edge cases not covered by standard tests?
* **Relevant Context**: All rules R1 through R8, and edge cases like Python's `bool` subclassing `int`.
* **Resolution**: Verified all rules against the codebase. Added `tests/test_edge_cases.py` to specifically test:
  - Exact boundary conditions (`10:00:00.000Z` $\rightarrow$ 3600s).
  - Strict rejection of boolean tokens (`tokens: True` rejected as `invalid_request`).
  - Month/midnight rollovers.
  - Oversized tokens exceeding total tier capacity.
* **What Changed as a Result**: Test suite expanded from 26 to 31 tests; 100% pass rate confirmed.

---

### Question 6: CLI Argument Formatting in PowerShell
* **Question**: Why did running `python -m src.cli <requests.jsonl> <limits.json> <decisions.jsonl>` produce a `RedirectionNotSupported` error and `FileNotFoundError`?
* **Relevant Context**: PowerShell shell syntax vs. documentation placeholder notation.
* **Resolution**: Explained that `<>` characters are documentation placeholders which PowerShell parses as redirection operators. Furthermore, sample input files did not exist in the root folder.
* **What Changed as a Result**: 
  1. Created sample [`limits.json`](file:///C:/Users/Mahmoud%20Al-Tous/.gemini/antigravity-ide/scratch/quota-rate-limiter/limits.json) and [`requests.jsonl`](file:///C:/Users/Mahmoud%20Al-Tous/.gemini/antigravity-ide/scratch/quota-rate-limiter/requests.jsonl) in the root directory matching BRIEF.md examples.
  2. Updated all documentation to show clean command syntax (`python -m src.cli requests.jsonl limits.json decisions.jsonl`).

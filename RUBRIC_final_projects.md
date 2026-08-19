# Grading Rubric — Final Three Projects

**For Mahmoud. You get this on day one, before the first brief.**

Three projects, one per week, finishing 10 September. Each is graded out of 10 against this rubric — the same five axes, the same bands, every time. After each grade we sit down, go through it line by line, and you go into the next project knowing exactly which cells to move.

The expected trajectory is **~2.5 → 4+ → 6.5+**. A low first score is not a failure; it is a baseline. What is being measured is the slope.

## Two things to be clear about up front

**Using AI is expected, not penalised.** AntiGravity will write most of the code and that is what it is for. Nothing in this rubric asks you to write code by hand, and nothing rewards you for pretending you did.

**What is graded is the part the AI cannot do for you:** understanding the problem, deciding what correct means, checking that the result is actually correct, reporting it honestly, and being able to explain it. A tool that writes perfect code for the wrong requirement has produced nothing of value. That gap is the whole subject of these three weeks.

---

## The five axes — 2 points each

### 1. Problem understanding

*Did you understand the problem before building, and can you prove you did?*

| Score | |
|---|---|
| **0** | Started building straight from the brief. No restatement, no questions asked. |
| **0.5** | Restated the brief as paraphrase. No gaps or ambiguities identified. |
| **1** | Identified some ambiguities. Asked at least one question that changed what you built. Assumptions listed. |
| **1.5** | Identified most ambiguities, including at least one non-obvious one. Assumptions carry consequences — what happens if each turns out wrong. Noticed where the spec departs from the standard way this problem is usually solved. |
| **2** | All of the above, plus you can state what you refused to decide alone and why. **Test: could a competent stranger build the same system from your written understanding alone?** If yes, this is a 2. |

### 2. Working code

*Does it work? Judged against acceptance tests you do not see, on data you do not have.*

| Score | |
|---|---|
| **0** | Does not run from a clean clone, or fails most hidden tests. |
| **0.5** | Runs. Passes fewer than half. |
| **1** | Passes most. Fails on edge cases. |
| **1.5** | Passes all but one or two — **and those failures are ones you had already documented as known limitations.** |
| **2** | Passes every hidden test. Runs from a clean clone using the commands in your README, on the first attempt. |

Note the 1.5 band: knowing what is broken and saying so scores higher than not knowing. That is deliberate.

### 3. Verification

*Did you check it yourself, or did you assume?*

| Score | |
|---|---|
| **0** | No tests of your own, or tests that cannot fail. Claims with nothing behind them. |
| **0.5** | Tests exist but assert little, or were never run against input designed to break them. |
| **1** | Real tests covering the main path plus at least one failure case. You can point to a test that caught something. |
| **1.5** | Tests cover the edge cases in the spec. You found and fixed at least one defect in code the AI generated, and can show me which. |
| **2** | Every claim you make traces to a command I can run. **You can break something on purpose and show me the test failing.** Your AI log shows what you checked and how. |

### 4. Honest reporting

*Does your document describe the system you actually built?*

| Score | |
|---|---|
| **0** | The document describes something that does not exist. Numbers with no source. |
| **0.5** | Broadly accurate, but contains at least one claim the code contradicts, or one number that no script produces. |
| **1** | Accurate. States what works. Limitations mentioned in general terms. |
| **1.5** | Accurate and specific about what does *not* work. Every number regenerable. What you cut is stated plainly. |
| **2** | A reader who was not there could tell exactly what to trust and what not to. Nothing overstated, nothing omitted — **including at least one thing that counts against you.** |

That last clause is the point of the axis. A report where everything passes and nothing is qualified is not a strong report; it is an unverifiable one.

### 5. Defence

*Can you account for what you shipped?*

| Score | |
|---|---|
| **0** | Cannot explain parts of your own repository. Answers *what* when asked *why*. |
| **0.5** | Explains the happy path. Cannot account for design choices or for AI-generated sections. |
| **1** | Explains most decisions. Can name one alternative you rejected and why. |
| **1.5** | Explains every part, generated code included. Handles a challenge without falling back on "the AI wrote that." |
| **2** | Answers *why* throughout. Concedes cleanly when you are wrong rather than defending a bad line. Can defend a decision against a plausible alternative. **Nothing in the repository you cannot account for.** |

---

## Hard caps

Some things put a ceiling on an axis no matter how good the rest is. These are not punishments — they are the specific failures this rubric exists to prevent, and knowing where they are is the advantage of having the rubric.

| If | Then |
|---|---|
| A number appears in a document and no script produces it | **Honest reporting capped at 0.5** |
| A test cannot fail, or a metric cannot go down | **Verification capped at 0.5** |
| The expected answers are present in the code being tested | **Working code capped at 0.5** |
| Anything in the repository you cannot explain | **Defence capped at 1** |
| Implementation code committed before `UNDERSTANDING.md` | **Problem understanding capped at 1** |

---

## Deliverables — the same six, every project

The order matters. This is the spine, and it does not change between projects.

1. **`UNDERSTANDING.md`** — the problem in your own words, what is missing or ambiguous, the questions you asked and what the answers changed, and your assumptions with the consequence of each being wrong.
2. **Your own test suite** — written before the implementation.
3. **The implementation.**
4. **`EVIDENCE.md`** — what you measured, what counts as correct, and the command that regenerates every number you quote.
5. **`AI_LOG.md`** — what you delegated, what came back, and how you verified it. Short entries. This is a graded deliverable, not a confession.
6. **`QUESTIONS.md`** — every question you asked anyone, when, and what changed as a result. **Asking scores points. Not asking, and guessing instead, costs them.**

Then the defence session.

---

## How the three projects differ

The rubric is identical. What escalates is how much of the problem is yours.

| | You are given | You produce |
|---|---|---|
| **Project 1** | A complete specification | Understanding, tests, code, evidence, defence |
| **Project 2** | An ambiguous request | The specification as well — signed off before you build |
| **Project 3** | A goal | The specification, the definition of done, and evidence sufficient for someone who was not there |

Each removes one support. The final project is the one that shows whether this transferred or whether you learned one problem.

---

## One last thing

Every one of these specifications will differ in some detail from the way the problem is normally solved. That is deliberate. The standard implementation — the one an AI produces immediately and confidently — will fail the hidden tests.

There is no way through that except reading the requirements properly. Which is the entire argument, and the reason understanding is worth 80% of the work while the code is the remaining 20%.

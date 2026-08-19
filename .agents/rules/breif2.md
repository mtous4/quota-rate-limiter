---
trigger: always_on
---

# Project Source of Truth

@BRIEF.md

BRIEF.md is the authoritative source of truth for this project.

Always consult BRIEF.md before planning, implementing, modifying, testing, or reviewing anything in this project.

Follow the specification exactly as written.

Do not:
- invent requirements
- change specified behavior
- replace specified rules with standard industry behavior
- sort requests unless explicitly required
- introduce rolling windows
- assume denied requests consume no quota
- do any commit on source control without my accept 

Pay particular attention to R1, R2, R4, and R8.

If existing code conflicts with BRIEF.md, BRIEF.md takes priority.

Before making implementation decisions, verify them against BRIEF.md.
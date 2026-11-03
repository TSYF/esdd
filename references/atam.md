# ATAM — architecture evaluation (Phase 5)

ATAM stress-tests the ADD output before handoff. It is an evaluation
method, not a redesign session: findings feed risk themes, and only
blocking risks loop back to ADD.

## 1. Scenario walkthrough

For each QAS (highest BV×TR first), trace the scenario through the
candidate architecture with a subagent (see SKILL.md briefs):

- Follow stimulus → artifact → response through the C4 and dynamic views.
- Mark each QAS: **achieved** (structure guarantees the measure),
  **addressed** (measure plausible but unproven — usually needs a
  prototype or test task), or **at risk** (structure fights the measure).

## 2. Classify findings

Use these sentence templates — they force precision:

- **Risk**: "Under `<condition>`, `<element>` may fail `<QAS>` because
  `<uncertainty>`."
- **Non-risk**: "`<element>` meets `<QAS>` because `<structural reason>`
  — no action."
- **Sensitivity**: "The architecture's ability to meet `<QAS>` is
  sensitive to `<parameter>`; small changes in it swing the outcome."
- **Tradeoff**: "`<decision>` improves `<QA-1>` at the cost of `<QA-2>`
  (cited: ADR-NNNN)."

Risks cite the specific decision (ADR) that created them. A risk with no
causing decision is really an unmade decision — send it back to ADD as an
iteration goal, not a risk.

## 3. Severity

- **blocks goal** — a proposal.md Goal or an H-BV QAS is in jeopardy.
  → new ADD iteration: "mitigate <risk>". Do not hand off.
- **needs mitigation** — an M-BV QAS degraded, or retrofit cost high.
  → hand off only with the human's explicit acceptance; record as a task.
- **watch** — L-BV impact or improbable condition. → list it, move on.

## 4. Risk themes

Cluster risks by shared root cause and name each theme:
"All three scalability risks trace to the single-writer decision
(ADR-0007)." Themes — not individual risks — are what the human
prioritizes. A theme usually maps to exactly one ADD iteration goal.

## Output

Fill the ATAM Evaluation section of `specs/<slug>/design.md`:
walkthrough results table, classified findings, themes, and the
loop-back decision (new ADD iteration / proceed to handoff). Run
`esdd phase atam --done --spec <slug>` when the human signs off.

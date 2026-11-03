# Utility Tree (Phase 3)

Maps each ASR to one or more **Quality Attribute Scenarios (QAS)** and
ranks them. The tree is ADD's priority queue (highest-value/highest-risk
QAS get designed first) and ATAM's walkthrough script later.

## QAS anatomy — all six parts, every time

| Part | Rule of thumb |
|------|---------------|
| Source | actor, another system, time, the operator |
| Stimulus | a concrete event, not a vibe |
| Artifact | name the part of the system stimulated |
| Environment | normal / peak / startup / degraded / recovery |
| Response | observable behaviour, active voice |
| Response Measure | a number with a unit and a window |

Weak: "the system should be fast under load."
Strong: "During a Black-Friday peak (10x normal RPS), the checkout API
(artifact) responds (response) with p99 ≤ 800ms and 0 5xx (measure) for
sustained 6h (window)."

Measurable response measures cheat sheet: latency percentiles + window,
error budget/allowed failure rate, throughput, RPO/RTO, MTTR, max
recovery steps, data freshness lag, cost per 1k requests.

## Ranking (human validation loop)

For every QAS propose two grades, **with a one-line rationale each**, then
ask the human to confirm or override. Never grade silently — the rationale
is what the human can actually disagree with.

- **Business value (BV)**: H — a proposal goal fails without it; M — goal
  degraded but survives; L — nice to have.
- **Technical risk (TR)**: H — wrong architecture is expensive or
  impossible to retrofit; M — retrofit painful but bounded; L — any
  reasonable design handles it.

Display in the tree as `QAS-n (BV,TR)` under its quality attribute branch.
The ADD iteration order: H/H first, then H/M and M/H, then the rest.

## Utility tree shape

```
                    <SYSTEM>
        ┌───────────┼────────────┐
   Performance    Modifiability   Security
        │               │
  QAS-1 (H,H)     QAS-4 (H,M)
  QAS-2 (M,H)           │
                  QAS-5 (M,L)
```

Keep it in `utility-tree.md`. A spec with >12 QAS is a sign the ASR list
wasn't distilled — merge duplicates and drop L/L scenarios (record them as
non-goals in proposal.md instead).

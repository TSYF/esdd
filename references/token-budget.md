# Token budget (Phase 4 Step 5 and Phase 6)

Every ESDD task must fit in one agent context: **target ≤ 100k tokens,
soft limit 100k, hard stop 140k**. Above 140k the task is forbidden
unless the human explicitly signs off in writing (a note in the task's
annotations). Degraded agents make degraded architecture; the budget is a
quality gate, not a nicety.

## Estimation model

Code averages ~4 characters per token. A task's context is dominated by
what it must READ (existing code, docs, diagrams) plus what it writes,
plus tooling overhead:

```
est_tokens = chars(touched files) / 4 + 1500 × (number of touched files)
```

- `touched files` = everything in the task's `touches` globs: files read
  for context AND files created/modified. Underestimate honestly —
  globbing a directory pulls everything under it.
- The 1500/file overhead covers paths, tool chatter, and the task brief.

## Setting estimates

```bash
esdd estimate --spec <slug> --set
```

Computes from `touches`, writes `token_estimate`. Files matching no glob
are reported as missing — fix the glob or create the file. Tasks with
nothing to touch (pure research/decision tasks) should get a manual
`token_estimate` under ~20k instead of `touches`.

## Verdicts

| Estimate | Verdict | Action |
|----------|---------|--------|
| ≤ 100k | ok | none |
| 100k–140k | SPLIT | decompose before handoff |
| > 140k | HARD-STOP | split; if the human insists, they sign off by adding a `HARDCAP-APPROVED: <reason>` annotation to the task — `esdd verify` enforces this marker |

## Splitting strategies

Split along the interfaces defined in design.md — each side of an
interface is a natural seam:

1. **By interface** — producer task and consumer task, contract pinned in
   design.md first. Best independence profile.
2. **By scenario** — one QAS's happy path per task; edge cases separate.
3. **By file cluster** — only when the code itself suggests the seam.
   Check the split didn't just move the blocking edge.

After splitting, re-run `esdd estimate --set` and `esdd matrix` — a split
that changes the dependency structure may change the blocking-edge graph
and the agent work order.

## The handoff gate

`esdd verify --spec <slug>` enforces: every actionable task carries an
estimate under the hard limit (or a human sign-off), blocking edges are
acyclic and resolvable, the index task's `adrs` UDA matches files on
disk. A spec that doesn't pass `verify` is not handed off — fix or split.

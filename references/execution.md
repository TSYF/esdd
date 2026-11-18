# Execution — post-handoff task dispatch (Phase 6→7)

How to run the materialized task graph without the failure modes that
burned the reference case (below). These rules are enforced through task
annotations and briefs, not vibes.

## The six standing rules

1. **Spike-first.** Any task whose estimate rests on "first run of new
   tooling" or "two sources of truth must be compared" gets a preceding
   spike ticket: no code deliverable, est 5–10k, output = an evidence
   report appended to the task's annotations. The engineering ticket then
   cites the spike's evidence instead of re-deriving it.
2. **Split by morphology, not artifact.** Decision / harness / deliverable
   are different cognitive loops with different failure paths — one task
   per morphology. An artifact-shaped split ("the DDL part" / "the test
   part") still bundles all three loops in each half.
3. **Standing workbench bring-up.** DB/tooling prerequisites live in a
   committed bootstrap script; every environment-touching task runs it
   first and never re-derives the recipe. Env facts the orchestrator
   learns mid-flight get annotated onto the affected tasks immediately —
   not kept in the orchestrator's head.
4. **Step-verified reporting.** Every brief numbers its steps; each step
   produces one artifact + one report line, so a dead agent leaves
   recoverable state and orchestrator forensics costs ≈ zero. Silent
   agent deaths (no artifacts, no report) cost the reference case ~2×.
5. **First-red triage.** If the FIRST attempt on a task (or step) fails,
   triage before any retry — split / spike / HUMAN. Never blind-retry.
   The human option exists because "tool internals contradict their
   documentation and iterative debugging over an unfamiliar system is
   required" is precisely where agents degrade fastest relative to a
   human with the tool open.
6. **Estimator calibration.** `token_estimate` (see token-budget.md) is a
   floor for volume-only tickets. Manually inflate — or better, split —
   when uncertainty work is present; estimates computed from globs
   matching not-yet-existing files are 0 and need honest manual values.

## Concurrency

- Agents editing one worktree in parallel: pre-edit shared files
  (registries, shared specs, config) as separate orchestrator commits
  BEFORE dispatching, and brief every agent with an explicit do-not-touch
  list; instruction to report (not edit) if a shared-file change becomes
  necessary.
- Unique scratch names per agent for DB/cloud resources; teardown in
  `finally`.
- Long-running evidence loops (soak, flake ledgers) record the git sha
  per iteration — fixes mid-run become attributable by comparing flake
  rates across the sha boundary.

## Human-only decision points

Collect them as they surface (capacity loss vs leniency, core-logic
changes, merge decisions) and present them batched with evidence and a
recommended option — the human ratifies; agents never self-waive
(`worker:human` tasks and non-waivable gates stay out of agent hands by
design, see taskwarrior.md).

## Reference case

drizzle-migration (2026-11): a scaffold+proof task estimated at 29k
tokens consumed five dispatch attempts — two silent deaths with zero
artifacts, one context-wedged mid-analysis, two restart kills — because
it bundled an architecture ruling, tool-misdeparse debugging, and
deliverable engineering into one ticket. Adopted rules 1–6 above;
execution after adoption ran the remaining ~20 tasks (5-domain swaps,
gates, soak) with zero silent deaths. Full writeup: that workspace's
`.esdd/specs/<slug>/execution-notes.md`.

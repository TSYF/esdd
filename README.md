# esdd — Exhaustive Spec-Driven Development

An agent skill that turns "build me X" into a verified architecture and a
graph of agent-sized tickets. It runs in four steps:

1. **Grill** the human into a product spec: stories with Given/When/Then
   scenarios plus an Impact Map.
2. **Derive** quality attributes (QAW, ranked utility tree).
3. **Design** the architecture with ADD (C4 + PlantUML diagrams, three-level
   MADR ADRs) and stress-test it with ATAM.
4. **Decompose** it into INVEST-clean Taskwarrior tickets. Each ticket stays
   under a 100k-token budget and is assigned to an agent or a human.

`SKILL.md` is the source of truth for the method. This README covers setup
and the day-to-day entry points.

## Requirements

| Tool | Needed for | Without it |
|------|-----------|------------|
| Python 3 | `scripts/esdd`, the deterministic CLI (stdlib only) | required |
| Taskwarrior (3.x) | the task graph (`depends`, workers, estimates) | tasks go to a `tasks.md` ledger; the graph is never materialized |
| PlantUML | rendering `diagrams/*.puml` | sources are still the spec; design.md notes they're unrendered |

The CLI creates an empty `.esdd/tasks/` taskrc when you have no Taskwarrior
config file, so a fresh Taskwarrior install works without setup.

## Install

The skill lives at `~/.agents/skills/esdd`. To install the four specialist
agents as subagents in your harness:

```bash
mkdir -p .claude/agents && ln -s ~/.agents/skills/esdd/agents/*.md .claude/agents/   # Claude Code
mkdir -p .agents/agents && ln -s ~/.agents/skills/esdd/agents/*.md .agents/agents/   # other harnesses
```

Without that step, the skill still delegates: it spawns a general subagent
and uses the agent files as its brief.

## The four specialists

| Agent | Owns | Phases |
|-------|------|--------|
| `esdd-po` | grills the human into `proposal.md`: goals, actors, impacts, stories with GWT, Impact Map. Business language only | 1 |
| `esdd-architect` | QAW → ASRs, ranked utility tree, ADD (C4 L1–4, diagrams, ADRs), ATAM | 2–5 |
| `esdd-fde` | tickets from the converged design: INVEST, GWT-derived briefs, estimates, `depends`, `worker:human` | 6 |
| `esdd-reviewer` | gates: `design`, `tickets`, `code` — optional/on-request (experimental; method in `references/review.md`). Never edits | gates |

All human contact stays with the orchestrator. A specialist that needs an
answer stops and returns the question instead of guessing. Business gaps
found later are routed back to the PO.

## Three ways in

**Full path.** For a new feature that needs architecture work:
"ESDD this feature: per-endpoint rate limits, shared Redis, ≤5ms p99."

**From an existing spec.** Copy a refined Jira ticket, a Taskmaster
tasks.json, or a written proposal into `.esdd/specs/<slug>/sources/` (or
run `esdd po import <file> --spec <slug>`). The PO maps it into
proposal.md, has you sign off on any acceptance criteria it converted into
GWT, and grills only the gaps. The Architect continues from there.

**Lite path.** For a decided plan, like one from a coding agent's plan
mode: `esdd po import <file> --spec <slug>` → PO → FDE → `esdd review
--gate tickets`. It skips the utility tree, ADRs and ATAM but keeps the
GWT contract, the token budget and the interfaces-before-tasks rule. Use
the full path if the plan hides an architectural decision.

## What a spec produces

```
.esdd/
├── adrs/          directory-level ADRs (global ones: ~/.esdd/adrs)
├── design.md      shared C4 context + container views
├── tasks/         Taskwarrior data (project=<ws>.<proj>.<slug>)
├── specs/<slug>/
│   ├── proposal.md     stories + GWT + Impact Map
│   ├── utility-tree.md drivers, ASRs, ranked QAS
│   ├── design.md       ADD architecture + ATAM findings
│   ├── diagrams/*.puml C4 + sequence/class/state/ER
│   ├── adrs/NNNN-*.md  spec-level MADR ADRs
│   ├── sources/        imported external specs/plans
│   ├── matrix.md       blocking-edge matrix (generated)
│   ├── tasks.md        ledger, only when Taskwarrior is missing
│   └── review-<gate>.md review gate reports
```

## CLI (`scripts/esdd`)

```bash
esdd init [--graph-nav none]         # scaffold .esdd/ at the workspace root
esdd doctor                          # check workspace, Taskwarrior, env
esdd spec new <slug> --project <p>   # scaffold a spec + its Taskwarrior index task
esdd po import <file> --spec <slug>  # external spec/plan → sources/, PO import mode
esdd adr new --level spec --spec <slug> --title "Use Redis"
esdd estimate --spec <slug> --set    # token estimates (ok ≤100k, SPLIT ≤140k, else HARD-STOP)
esdd matrix --spec <slug> --out .esdd/specs/<slug>/matrix.md
esdd verify --spec <slug>            # handoff gate
esdd review --gate tickets --spec <slug>   # deterministic review; writes review-tickets.md
esdd review --gate code --spec <slug> --task <uuid>
esdd tw -- next                      # the agent work queue
```

`spec list`, `matrix`, `estimate`, `verify` and `review` accept `--json`.
`review` exits 0 (pass), 1 (violations) or 2 (usage); it writes
`review-<gate>.md`, stamps per-gate rounds in `.esdd/state.json`, and flags
a violation unfixed for two consecutive rounds as `escalate: true`.
`phase --strict` exits 2 when prerequisites are missing. See the CLI table
in `SKILL.md` for the full list.

## Repository layout

```
SKILL.md         the method: hard rules, phases, briefs, degradation
agents/          the four specialist definitions (harness-agnostic markdown)
references/      per-phase method reference (product, qaw, add, atam, invest, ...)
assets/          templates: proposal, utility tree, design, ADR, task brief, PlantUML theme
scripts/esdd     deterministic CLI
tests/smoke.py   self-bootstrapping smoke harness
evals/           skill evaluation prompts
```

## Tests

```bash
python3 tests/smoke.py    # smoke harness (Taskwarrior 2.6.1)
```

Covers: scaffolding, slug validation, batch import, blocking edges, matrix
(+ cycle detection), estimate math, the verify gate incl. HARDCAP-APPROVED,
three-level ADRs, phases (`--strict`), graph import/retro, the three
`review` gates (incl. planted-violation escalation and delta stamps), and
`--json` outputs. The harness bootstraps its own sandbox under
`/tmp/opencode/esdd-test` and is safe to re-run.

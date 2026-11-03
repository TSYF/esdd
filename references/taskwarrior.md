# Taskwarrior conventions (all phases)

ESDD never calls `task` directly — always through the wrapper, which
finds the nearest `.esdd` upward and injects the data location and UDAs:

```bash
esdd tw -- <normal task arguments>
esdd tw --batch -- <arguments>     # no confirmation prompts (scripts only)
```

## Project hierarchy

`project:<workspace>.<project>.<feature>` — dot-separated, native
Taskwarrior nesting. Workspace = the directory that contains `.esdd`
(auto-derived from its name), feature = the spec slug. Slugs are
lowercase-hyphen only: dots would corrupt the hierarchy.

Taskwarrior ids are per-database and get recycled; scripts must use uuids
in `depends`, humans may use short ids.

## UDAs (injected by the wrapper)

| UDA | Type | Meaning |
|-----|------|---------|
| `adrs` | string | Index tasks only: comma-separated `NNNN-slug` entries matching `specs/<slug>/adrs/*.md` |
| `touches` | string | Comma-separated file globs (repo-root-relative) the task reads/writes |
| `token_estimate` | numeric | Estimated context tokens; set by `esdd estimate --set` |
| `worker` | string | `agent` (default) or `human` |

## Index task (one per spec)

Created by `esdd spec new`. `+spec` tag, project leaf = spec slug,
description `<slug> :: spec index`. Holds the spec's ADR list in its
`adrs` UDA. It is never worked; it exists so `esdd tw -- +spec` lists
every spec's front door and `verify` can check ADR sync.

After each `esdd adr new --level spec`:

```bash
esdd tw -- <index-uuid> modify adrs:"0001-foo,0002-bar"
```

## Creating tasks in bulk

Prefer one `task import` over many `add` calls — fewer confirmations,
atomic, reviewable. Write JSON, then:

```bash
esdd tw -- import /tmp/tasks.json
```

```json
[
  {
    "description": "Implement PricingEngine core",
    "project": "shop.core.checkout",
    "tags": ["checkout"],
    "touches": "src/pricing/**,src/pricing/*.test.ts",
    "worker": "agent",
    "annotations": [
      {"description": "Goal: ... Context: design.md#pricing ... Verify: pnpm test pricing"}
    ]
  },
  {
    "description": "Wire PricingEngine into OrderController",
    "project": "shop.core.checkout",
    "depends": "<uuid-of-previous-task>"
  }
]
```

Set `depends` after creation when you need uuids of freshly imported
tasks (match by description via `task export`).

## Blocking edges

`esdd tw -- <id> modify depends:<other-uuid>` — "this task is blocked by
that one". Workable blockers-first: never create a cycle
(`esdd matrix` warns). For cross-spec edges, both tasks must exist in the
same `.esdd/tasks` database — they do, because tasks always live in the
workspace root's `.esdd`.

## Briefs

First annotation of every actionable task, ≤ ~600 tokens, per
`assets/task-brief-template.md`. Detail belongs in design.md; the brief
points at it.

## Human-owned tasks

`worker:human`. They are excluded from agent dispatch; `esdd verify`
prints them as a plain-English work order at handoff.

## Useful queries

```bash
esdd tw -- next                              # what's actionable now
esdd tw -- blocked                         # waiting on something
esdd tw -- project:shop.core.checkout      # one spec's graph
esdd tw -- +spec                           # all spec index tasks
esdd tw -- worker:human status:pending     # the human's queue
esdd matrix --spec checkout                # dependency matrix + cycle check
```

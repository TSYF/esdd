# Retro — retroactively documenting an existing repo (workspace level)

Retro brings an existing codebase into ESDD scaffolding **without** a
product loop: no proposal.md, no QAS, no Taskwarrior tasks. Its output is
*"Technical Context"* — the ground truth later phases (QAW, ADD) consume.

```
retro produces                          retro must NOT produce
─────────────────                       ──────────────────────
.esdd/design.md       (C4 L1+L2)        proposal.md            (needs human loop)
.esdd/adrs/NNNN-*.md  (inferred)        utility-tree QAS       (needs human loop)
.esdd/graph/<src>/    (cached source)   Taskwarrior tasks      (no specs exist)
catalogue.md          (elements/interfaces)
```

## The one governing constraint: tokens

Retro is the heaviest phase in ESDD — a whole repo's worth of context. The
graph/navigation tools exist precisely so we never pay that cost in raw
code reads. The protocol below is written to be enforced, not suggested:

1. **Never re-run the source tooling.** Import once (`esdd import`);
   everything after reads the cached snapshot.
2. **The orchestrator never reads the snapshot directly.** It may only
   hold the manifest, the catalogue skeleton, and design.md. Element and
   edge data flows through sub-agents.
3. **Raw code is a fallback**, used only for spot-checking a claim a
   sub-agent derived from the graph, and only via narrow grep/read with a
   stated purpose.

## Phase protocol

### Step 0 — Source selection (human, once)

At `esdd init` the human picked `GRAPH_NAV`. Confirm it is usable:

- `esdd import --list-sources` — is a snapshot already cached?
- If not: `esdd import --source <chosen> --path <tool output>` copies the
  output into `.esdd/graph/<source>/` (a directory copies recursively; a
  single file keeps its name unless `--snapshot` is passed, which
  registers it as that source's normalized `snapshot.json`). The CLI
  validates a cached `snapshot.json` and prints element/edge counts.
- The source is interchangeable — codegraph, graphify, falkordb/neo4j
  (query the MCP, dump the result as JSON), understand, groma, custom —
  whatever navigates this repo cheapest. For MCP-backed sources the
  orchestrator queries the MCP and writes the normalized snapshot itself,
  then registers it with `esdd import --source <name>`.
- `none`/no graph available ⇒ the heuristic path (Step 2b) with plain
  grep/read; budget roughly 2× the tokens and say so to the human.

### Step 1 — Normalize into snapshot.json

One minimal schema, source-agnostic. It is deliberately small: every
downstream agent reads this, so every source maps onto it.

```json
{
  "elements": [
    {"id": "svc-checkout", "name": "checkout", "kind": "container",
     "tech": "TypeScript, Node", "path": "services/checkout/**",
     "description": "one line"}
  ],
  "edges": [
    {"src": "svc-checkout", "dst": "db-orders", "type": "reads-writes"},
    {"src": "person-customer", "dst": "svc-checkout", "type": "uses"}
  ],
  "meta": {"source": "codegraph", "captured": "2026-11-05", "repo": "..."}
}
```

- `kind` ∈ `person | system | container | component | datastore | queue`
  (C4 vocabulary — the diagrammer consumes it directly).
- `path` is optional per element but gold when present: it localizes the
  element to file globs without re-deriving that anywhere else.
- A sub-agent ("normalizer") maps the cached source format → this schema
  if the import didn't already include a valid `snapshot.json`.

### Step 2a — Graph path (snapshot.json valid)

Run the explorer sub-agent, one call, with this brief shape:

```
Read .esdd/graph/<source>/snapshot.json (use offset reads; do NOT load
raw code). Topological sweep, in this order:
  1. persons (kind=person) and their key edges
  2. systems vs. containers: element boundary split
  3. datastores/queues (they anchor the boundary and the ER later)
  4. remaining components, grouped by their container parent
Write .esdd/graph/<source>/catalogue.md :
  ## Elements        (table: id, kind, tech, path, one-line responsibility)
  ## Boundaries      (proposed System Boundary groupings with rationale)
  ## Interfaces      (one row per high-traffic edge: contract guess)
  ## Unresolved      (every claim with confidence < high, and why)
Return ONLY: counts of sections + the top-5 highest-confidence boundary
claims as bullets. No catalogue content in your reply.
```

*Interface entries here are **observed** contracts (what the code shows
today), not designed ones — mark each `observed`.*

### Step 2b — Heuristic path (no graph)

Cheaper tools preserve tokens even without a graph. Escalate downward:

- `ls`/`tree` depth ≤ 3 → directory structure is the first-cut boundary.
- Classify top-level dirs: monorepo? `services/`? `packages/`?
  Convention beats invention — pick labels matching what's found.
- For each candidate container: read ONE entrypoint (or package.json /
  pyproject.toml / go.mod) — not the module tree.
- ADR sources: `docs/`, `CHANGELOG`, commit messages (`git log --oneline
  --grep`), and existing `*.md` docs mentioning **why**.

Hard ceiling guidance: if the heuristic sweep exceeds ~40k tokens of
orchestrator + sub-agent context combined, stop and tell the human the
repo needs a graph tool before retro is viable. Don't take a repo beyond
~15 major elements without a graph.

### Step 3 — Inferred MADR ADRs (directory level)

The catalogue's `Boundaries` and technical choices become ADRs at
**directory level** (`.esdd/adrs/NNNN-*.md`), because they describe this
repo's conventions, not any one spec:

- One ADR per significant, hard-to-reverse choice actually observable in
  the snapshot: "monolithic deployment", "event-driven via Bus",
  "TypeScript across all containers", "X as sole datastore".
- Cap the first pass at **8 ADRs** — the eight most load-bearing
  decisions. Depth over breadth; more can be inferred later per-spec.
- Status line: `inferred`, and the Links section must record the
  evidence: which catalogue rows / snapshot elements justify it, plus
  confidence (`high | medium | low`). This is what separates a retro
  MADR from a real one — nobody consulted the deciders.
- A choice with only weak evidence goes in catalogue.md `Unresolved`,
  not in an ADR. An inferred ADR is cheap to supersede; a fabricated one
  lies to every future spec that cites it.
- `esdd adr new --level directory --title "..."`, then edit status to
  `inferred` and append evidence links.
- Existing ADRs (any level) always outrank inferred ones: check
  `esdd adr list` first and never re-ADR a decision already accepted.

### Step 4 — design.md + diagrams (shared workspace level)

Delegate to the diagrammer sub-agent:

- **C4 L1 Context** — persons, systems, external systems. Usually one
  file: `specs/_shared/1-context-retro.puml` (shared level since it
  spans all future specs).
- **C4 L2 Containers** — the boundaries from the catalogue, tech from
  element rows. `specs/_shared/2-container-<system>.puml` per system.
- Fill `.esdd/design.md` Overview text: provenance ("inferred from
  <source> snapshot, <date>, confidence per element marked") and the
  element/interface tables mirrored from catalogue.md. design.md may
  duplicate the catalogue's distilled tables; it must not paste
  snapshot data.

### Step 5 — Register and hand the report

- `esdd phase retro --done` (workspace-level; no `--spec` needed).
- Report to human (~one screen): sources cached, elements × boundaries
  counts, ADRs inferred with confidence spread, unresolved items that
  deserve a human's memory ("was the monolith decision ever contested?"),
  and the note that future specs' QAW will consume this as Technical
  Context.
- The human may correct anything; corrections edit catalogue.md /
  design.md / ADR statuses — re-running retro is unnecessary and
  forbidden (it would discard human corrections).

### Step 6 — Adopt + fix (on request)

Retro documents; it does not grade. When the human wants the debt list,
run `/ponytail-audit` (Ponytail, MIT) after Step 5. It returns a ranked
defect list; map severity to ESDD's language: must-fix ≈ blocks-goal,
should-fix ≈ needs-mitigation, nice ≈ watch. Must-fix items become GWT
stories through the lite path (PO → FDE → `esdd review --gate tickets`),
not edits to retro's artifacts — retro output stays descriptive, and the
audit never edits files. The human owns triage.

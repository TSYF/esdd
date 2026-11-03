# QAW — Quality Attribute Workshop (Phase 2)

The QAW converts product intent into **architectural drivers** and
**architecturally significant requirements (ASRs)**. It is deliberately
separate from design: no tactics, no patterns, no libraries in this phase.
Naming a solution now anchors the design before the drivers justify it.

## Step 1 — Architectural drivers (orchestrator-led, ~15 min)

Elicit and record in `utility-tree.md`:

- **Business goals** — the numbers from proposal.md's Goals, in the human's
  own words. These outrank every technical desire in every later tradeoff.
- **Constraints** — copy from proposal.md; grill for any new ones ("we must
  be on the EU region", "no new paid services").
- **Technical context** — what exists: stack, deployment topology, teams,
  things that cannot change this quarter. Read code for this if the repo
  disagrees with the human.

## Step 2 — ASR brainstorm (human loop)

Round-robin questioning. For each business goal ask: **"What could make
this fail at 10x? At 1/10 the budget? When the team doubles?"** Capture
answers verbatim as ASR seeds, then structure each into the table:

| Field | Question it answers |
|-------|---------------------|
| ASR | one sentence, testable direction |
| Stimulus | what arrives (load spike, new tenant, deploy, crash) |
| Response (seed) | what the system should do about it |
| Measure (seed) | how we'd know (rough is fine — QAS hardens it) |

Quality attributes to probe explicitly: performance, scalability,
availability, security, modifiability, testability, deployability,
observability, interoperability. Not all will matter; the probe list just
stops the human forgetting availability until production.

**Human loop exit criterion**: the human says the ASR list is complete —
read it back and ask "what's missing?". Two consecutive "nothing" answers
end the brainstorm.

## Output

- `utility-tree.md` sections: drivers (complete), ASR table (complete).
- Do NOT rank yet. Ranking happens against hardened QAS in Phase 3.
- If an ASR smells like a solution ("use Redis"), ask "what property does
  that buy us?" and rewrite as a quality ("cache invalidation within 5s").

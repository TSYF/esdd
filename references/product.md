# Product — Given/When/Then + Impact Mapping (Phase 1)

The product phase maps out the **corners of a requirement**: what changes,
for whom, observable when. It produces exactly two structures and refuses
to proceed without them:

1. User stories whose acceptance scenarios are **Given/When/Then**.
2. An **Impact Map** (goal → actor → impact → deliverable).

INVEST is deliberately **not** applied here. Stories may still be big and
coupled when they leave this phase — ticket-time refinement owns
INVEST (see references/invest.md). Premature INVEST split optimizes the
wrong artifact: product stories should describe outcomes, not agent
contexts.

## Grilling protocol

The interview extracts the corners in this order — worst-gap first:

1. **Why** — "What changes for the business when this ships? What number
   moves?" Answers become Goals. "The codebase is cleaner" is not a goal.
2. **Who** — "Whose behavior changes? Name the actors: end users,
   operators, other systems, other teams." Actors beyond end users are
   the ones most often forgotten.
3. **How** — "What will each actor do differently? What will they stop
   doing?" A behavior change, not a feature description. Impacts become
   the bridge between goals and stories.
4. **What** — "What do we build to cause that impact?" Deliverables
   become user stories.
5. For every story: **"Walk me through one concrete run."** — this is
   where the GWT comes from (below).

Keep the human's words verbatim in your notes; structure into the
artifact only after the pass. The grilling is done when **Open Questions**
is empty AND every Impact Map row traces end-to-end.

## Given/When/Then first

A story does not enter `proposal.md` until it has at least one GWT
scenario. GWT is the phase's primary artifact, not a decoration:

| Part | Rule of thumb |
|------|---------------|
| **Given** | the initial state or context — things already true |
| **When** | one action or event under the system's control |
| **Then** | an *observable* outcome — something a test or an inspector can see |

Weak: "the checkout should be fast and reliable."
Strong: "**Given** a cart with 3 in-stock items, **when** the customer
confirms checkout, **then** an order confirmation appears within 2
seconds containing the same 3 items at the shown prices."

- Multiple scenarios per story are normal: happy path + at least one
  edge or failure case. Scenarios, not stories, are what split later.
- The **Then** must be observable *without* reading source code. If you
  cannot observe it, it is not acceptance — it is implementation.
- Writing GWT is also the testability gate in disguise: an unobservable
  Then means the story is not understood yet.
- **The scenarios survive into execution**: every ticket the design
  decomposes into carries a `Verify`/`Done when` derived from the GWT of
  the story it implements (see assets/task-brief-template.md). If a
  ticket at handoff time cannot name its originating scenario, the story
  was never finished — go back, not around.

## Impact Mapping

After stories stabilize, walk the map in order and record it as the
`## Impact Map` table in `proposal.md`:

```
GOAL (why) → ACTOR (who) → IMPACT (how: behavior change) → DELIVERABLE (what: story)
```

Three tracing rules — they are the map's whole value:

- **Deliverable → impact**: a story with no row means it exists because
  someone thought it would be cool. Move it to Non-Goals or grill for
  its real impact.
- **Impact → actor**: an impact nobody can name for the actor is a
  hypothesis. Grill or park it in Open Questions.
- **Actor → goal**: actors that don't serve any goal are out of scope
  for this spec.

Impact rows are also QAW's seeds (Phase 2): each (goal, actor, impact)
row is a candidate ASR — "how could this fail at 10x?" hardens the row
into stimulus/response form. Recording the map cleanly here directly
cheaper-izes the QAW.

## Output discipline

- `proposal.md`: User Stories table (ID + story), Acceptance Scenarios
  (GWT per story), Impact Map table, Constraints, Open Questions.
- Exit criteria: Open Questions empty; every map row traced; every story
  has ≥1 GWT scenario; the human has signed off on the drafted artifact.
- Draft proposal.md in a sub-agent, then present it back to the human
  for sign-off before writing (see SKILL.md "Sub-agent briefs").

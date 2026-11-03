# ADD — Attribute-Driven Design (Phase 4)

ADD designs the architecture one iteration at a time, each iteration
driven by a quality-attribute goal, not by a layer checklist. Iterate
until the human declares the architecture complete, then hand to ATAM.

## The five steps, operationalized

### Step 1 — Review inputs, establish design purpose
Read: proposal.md, utility-tree.md (drivers + ranked QAS), all applicable
ADRs (spec → directory → global, in that order — the narrowest applicable
wins), existing `.esdd/design.md` and `specs/<slug>/design.md`. State the
design purpose aloud in two sentences.

### Step 2 — Establish iteration goal (human checkpoint)
Propose the goal from the top unaddressed QAS: "This iteration makes
QAS-1 (H,H) structurally true." The human confirms or reprioritizes.
Write it in the Iteration Goals Log.

### Step 3 — Choose elements to refine
List the architectural elements in play (from the current C4 views). New
spec with no elements: the element set is "the system". Otherwise pick the
smallest set whose decisions can satisfy the iteration goal.

### Step 4 — Choose design concepts
For each element, select tactics/patterns/libraries. Rules:

- **Every concept must cite what justifies it**: a QAS it serves, or an
  ADR it obeys. A concept justified by fashion gets grilled in Step 2 of
  the next iteration.
- **ADRs constrain**: if a choice contradicts an accepted ADR, write a new
  ADR that proposes superseding it (`esdd adr new --level spec`); never
  silently ignore an accepted ADR. Mark the superseded one `deprecated`
  with a link.
- Prefer boring concepts that the human's team already operates, unless a
  QAS ranks H and forbids them.

### Step 5 — Instantiate elements
Commit the decisions:

1. **design.md**: update Overview, add the Interfaces entries (contract /
   provider / consumers / failure modes), log the iteration.
2. **Diagrams**: create/update the C4 and dynamic views (see
   c4-plantuml.md). Delegate to a subagent with a tight brief — diagram
   text is verbose; keep it out of the orchestrator's context.
3. **ADRs**: `esdd adr new --level spec --title "..."` for every
   significant, hard-to-reverse choice. Trivial choices don't get ADRs.
4. **Tasks**: decompose the iteration's work into Taskwarrior tasks (see
   taskwarrior.md for the batch-import pattern). Each actionable task
   gets: project `<ws>.<proj>.<slug>`, `depends:` for its **blocking
   edges**, `touches`, a brief first annotation, and a `token_estimate`
   (`esdd estimate --set`). Workable blockers-first: a task may only
   depend on tasks that will already be done when it starts.
5. **Matrix**: `esdd matrix --spec <slug> --out specs/<slug>/matrix.md`.
6. **Human worker selection**: ask the human which tasks (if any) they want
   to execute themselves; set `worker:human` on those.

### Loop
Return to Step 2 with the next QAS. When all H and M QAS are structurally
addressed, ask the human whether to stop. If ATAM later finds a blocking
risk, a new ADD iteration starts with goal "mitigate <risk>".

## Interface discipline

An interface is *"a contractual specification indicating how information
should flow between elements and what other elements can depend on."*
Every interface gets a design.md entry BEFORE any task touching it is
created, and every such task's brief must reference the entry. Interfaces
are where task independence is won or lost — vague interfaces create
blocking edges.

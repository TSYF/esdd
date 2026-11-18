# INVEST — ticket refinement (ticket creation: ADD Step 5, re-checked Phase 6)

INVEST belongs at **ticket time**, not product time. Stories may arrive
from Phase 1 big and coupled — that is fine; they described outcomes.
Before design work becomes dispatchable work, it is refined into tickets
that each fit one agent context. Two letters matter most for ESDD:

- **Independent** — independent tickets have few `depends` edges, so
  multiple agents work in parallel. A ticket that can only start "after
  that other one" is a chain link, not a ticket.
- **Small** — smallness is the token budget's first line of defence. If a
  ticket can't stay under 100k tokens, it's too big, full stop.

## When this runs

- **ADD Step 5**, per iteration batch, as the batch is decomposed into
  Taskwarrior tickets.
- **Phase 6 handoff**, re-checked as a gate: `esdd verify` catches
  estimates and cycles; this checklist catches the rest.

## The checklist, per ticket

1. **Independent** — "What does this ticket need from other tickets to
   be startable? What breaks if it runs alone?" If the answer names
   another ticket, merge or split. Cross-ticket knowledge requirements
   become explicit `depends` edges — never implicit assumptions.
2. **Negotiable** — "Which part would you trade away if the architecture
   made it expensive?" If nothing is negotiable, it's a constraint:
   move it to design.md Constraints and re-slice the ticket.
3. **Valuable** — "What changes for the user when this ships?" If the
   answer is "the codebase is cleaner", it's a refactoring task: demote
   it to a subtask of the ticket whose value it protects, or drop it.
4. **Estimable** — `esdd estimate --spec <slug> --set` computes from
   `touches` (see token-budget.md). Unknown size = unknown scope; keep
   grilling before dispatch. Uncertainty work present? See
   execution.md rule 1 (spike-first) and rule 6 (calibration).
5. **Small** — one agent context: rough ceiling ~6 files, ~1200 LOC,
   ≤100k tokens. Bigger → split **vertically by acceptance criterion**,
   not horizontally by layer.
6. **Testable** — every ticket's brief carries a `Verify` and a
   `Done when` derived from the **originating story's GWT scenario**
   (proposal.md). A ticket that cannot name its GWT scenario means the
   story was never finished — send it back to proposal.md, don't invent
   a verification.

## Splitting strategies (when I or S fails)

- **By acceptance criterion / GWT scenario** — each scenario becomes its
  own ticket. Best profile: the scenarios share state, so order the
  `depends` edges accordingly.
- **By user role** — admin flow vs. self-serve flow.
- **By outcome** — "view the report" vs. "export the report".

Never split by layer ("frontend ticket", "backend ticket") — those have
the worst blocking-edge profiles and the least independent value.
Morphology-based splits (decision / harness / deliverable) are covered in
references/execution.md rule 2 and are the tool of choice for tickets
that are *technically* one outcome but *cognitively* three loops.

## Token-budget splits

For tickets whose `token_estimate` verdict is SPLIT (100k–140k) or
HARD-STOP (>140k), follow references/token-budget.md: split along
interfaces pinned in design.md, re-estimate, re-run matrix. Human
sign-off via a `HARDCAP-APPROVED` annotation is the only way a >140k
ticket survives the gate.

# INVEST — product grilling (Phase 1)

INVEST is the checklist every user story must pass before it enters the
utility tree. Two letters matter most for ESDD's agentic workflow:

- **Independent** — independent stories decompose into tasks whose blocking
  edges are few, so multiple agents can work in parallel. A story that can
  only be done "after that other one" is one task chain, not a story.
- **Small** — smallness is the token budget's first line of defence. If a
  story can't produce tasks under 100k tokens, the story is too big.

## Grilling protocol

Interview the human. One letter at a time, worst-gap first. For each story:

1. **Independent** — "What does this story need from other stories to be
   useful? What breaks if we ship this one alone?" If the answer names
   another story, merge or split.
2. **Negotiable** — "Which part of this story would you trade away if the
   architecture made it expensive?" If nothing is negotiable, the story is
   a constraint, not a story — move it to Constraints.
3. **Valuable** — "What changes for the user when this ships? How do we
   observe it?" If the answer is "the codebase is cleaner", it is a
   refactoring task, not a story. Demote it.
4. **Estimable** — "How would we know this is 2 days vs 2 weeks?" If the
   human can't say, keep grilling: unknown size = unknown scope.
5. **Small** — "Can one agent hold everything this story touches in one
   context?" Rough ceiling: ~6 files, ~1200 LOC touched (see
   token-budget.md). Bigger → split vertically by acceptance criterion,
   not horizontally by layer.
6. **Testable** — "Give me the Given/When/Then." No testable criterion, no
   story. The Verify step of every downstream task brief comes from here.

## Output discipline

- Every story has ≥1 acceptance criterion in Given/When/Then form.
- Fill the INVEST table in `proposal.md`; any cell that isn't ✓ gets a
  one-line note saying why, and what will fix it.
- The grilling is done when **Open Questions** is empty. Do not proceed to
  QAW with open product questions — ASRs derived from mush are mush.
- Draft the proposal in a subagent (see SKILL.md "Sub-agent briefs"), then
  read it back to the human for sign-off before writing `proposal.md`.

## Splitting strategies (when S or I fails)

- **By acceptance criterion** — each criterion becomes its own story.
- **By user role** — admin flow vs. self-serve flow.
- **By outcome** — "view the report" vs. "export the report".
Never split by layer ("frontend story", "backend story") — those have the
worst blocking-edge profiles and the least independent value.

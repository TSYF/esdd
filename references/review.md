# Review — on-request gates (experimental)

Review is deliberately **not** a standing gate in the critical path. The
mechanical part is the `esdd review` CLI; the judgment part is
`agents/esdd-reviewer.md` or a human, dispatched when someone asks.
Promotion to a standing gate requires an audition: in the eval loop, plant
a ticket brief whose `Verify:` does not derive from its story's Then; the
reviewer must catch it.

## The post-hoc principle

Gate after the fact what is cheap to check late; reserve pre-gates for
what is expensive to discover late.

| Check | When | Why |
|-------|------|-----|
| Ticket GWT trace (`US-n` → scenario → Verify/Done when) | **pre-gate** | Rework after execution is expensive; a ticket without its GWT is a product gap, not a code review finding |
| Interface exists before a ticket touches it | **pre-gate** | A missing contract becomes a cross-ticket blocking edge |
| Mechanical lint (brief fields, token band, worker, ADR status, diagram refs) | **`esdd review`** | Deterministic, no judgment, cheap to re-run |
| Interface contracts honoured, Then observably met, diff within touches | **post-execution** | Needs the code; run with revert rights after the task |
| Style, naming, design taste | post-execution, human | Not a gate |

Review never edits artifacts. Findings go to the owner; the owner fixes.

## `esdd review` — deterministic checks

```bash
esdd review --gate tickets --spec <slug> [--json] [--out review-tickets.md]
esdd review --gate design  --spec <slug> [--json] [--out review-design.md]
esdd review --gate code    --spec <slug> --task <uuid> [--json] [--run-verify]
```

- Exit `0` = pass, `1` = violations, `2` = usage error (same as `verify`).
- Writes `review-<gate>.md` into the spec directory unless `--out` is given.
- `--run-verify` is off by default; the code gate never executes a brief's
  command unless asked.
- `--json` emits `{gate, spec, pass, violations, checks, rounds, delta?}`.

### Gate `tickets` (the meat)

The CLI re-runs `esdd verify` internally, then per actionable task:

- the first annotation is a brief;
- the brief names a `US-n` that exists in `proposal.md` and has a
  Gherkin fenced block (`` ```gherkin ``);
- the brief carries `Verify:` and `Done when:`;
- every name in the brief's `Interface obligations:` line exists under
  design.md `## Interfaces`;
- the token verdict is ≤100k, or >140k with a `HARDCAP-APPROVED`
  annotation (100–140k is SPLIT and fails);
- `worker` is set.

Judgment rows (never auto-fail): `Verify`/`Done when` actually derive from
the story's Then, and INVEST per `references/invest.md`.

Lite profile: the spec has no utility tree, ADRs or ATAM by design. Do not
flag their absence, or tickets with no interfaces when design.md lists
none. Every other check still applies.

### Gate `design`

Mechanical subset only:

- `proposal.md` exists and its Impact Map is present (empty rows are a
  judgment row, not a failure);
- each `### QAS-n` section has the six parts (source, stimulus, artifact,
  environment, response, response measure) — no QAS sections yet is a
  judgment row;
- spec ADR statuses parse (a file with no `## Status` fails);
- design.md `## Interfaces` exists and is not still template placeholders
  (empty/placeholder is a judgment row);
- every concrete `diagrams/*.puml` reference resolves.

Judgment rows: numeric response measure, GWT → ASR → QAS → design trace,
ADR supersede/deprecate discipline, C4 element-name agreement, ATAM risk
citations.

### Gate `code`

Minimal mechanical subset for one executed task:

- the first annotation is a brief;
- the brief carries `Verify:` and `Done when:`;
- the `touches` globs resolve to files;
- with `--run-verify`, the brief's `Verify:` command exits 0 (recorded;
  never run by default).

Judgment rows: the GWT Then is observably met, design.md interface
contracts are honoured, the diff stays within `touches`. The
inert→enforced validation audit (`references/validation-audit.md`) is a
judgment item when the change replaces validation.

## Report format

`review-<gate>.md`:

```markdown
# Review: <gate> — <spec>

- **Date**: YYYY-MM-DD
- **Spec**: `<slug>`
- **Verdict**: pass|reject (derived)
- **Since last run**: <date>, <N> violations then

## Rounds

| round | date | fail | new | fixed | unfixed | escalated |
|-------|------|------|-----|-------|---------|-----------|
| 1 | YYYY-MM-DD | 0 | 0 | 0 | 0 | 0 |

## Checks

| rule | status | detail |
|------|--------|--------|
| brief-story | fail | task 7 '...': brief names no US-n |

## Violations

| rule | path | detail |
|------|------|--------|
| brief-story | task:1a2b3c4d | brief names no US-n |

## Escalate to human

- `brief-story` at `task:1a2b3c4d`: unfixed for two consecutive rounds.
```

`status` ∈ `pass | fail | skip | judgment`. A `pass` verdict is **derived**:
fail iff any row is `fail`. `skip` and `judgment` never fail a gate; they
are dispatched to the agent/human.

## Loop rule

Two automatic loops (fix, re-run) then the human decides. `esdd review`
mechanizes this: it stores per-gate rounds in `.esdd/state.json`; a
violation unfixed for two consecutive rounds is tagged `escalate: true`
and surfaced as "escalate to human". The third loop is not the agent's.

## Delta discipline

Every `esdd review` run writes a gate stamp to `.esdd/state.json`:
`gates.<gate> = {spec, last_run, git_rev, violations, rounds}`. Output
includes `since last run: <date>, <N> violations then`; the report and
`--json` include new/fixed/unfixed counts and lists for the last
transition. The code gate also prints
`git diff --name-only <git_rev>..HEAD -- <touches>`.

On re-dispatch, the reviewer reads the previous `review-<gate>.md` first
and examines only changed/unfixed items. Round history is capped at 10.

## Adversarial mode

When asked for an adversarial review, write the GWT scenario that breaks
the design (a new stimulus/environment/measure). If the design fails it,
feed the scenario back as an ATAM risk or a new QAS. Do not patch the
design in review and do not weaken the scenario to make it pass.

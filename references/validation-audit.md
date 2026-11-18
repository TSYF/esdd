# Validation audit — replacing dead validation with real validation (per-spec phase, usually it-5/6)

When a spec replaces **inert** validation (registered but never
enforced: the old layer parsed-and-discarded, coerced silently, or
never ran) with **enforced** validation (schema-checked at every
binding), the enforcement itself is a behavior change. Old clients,
integrations, and tests may have learned to rely on the looseness —
what used to squeak through must now fail; what used to 500 must now
400 (or vice versa). Audit BEFORE the merge gate; the human ratifies
one disposition per route. Never "ship and watch".

## The audit ticket

One agent task, mechanically scoped, placed just before the merge gate
(usually it-5 or it-6). The creative act already happened when the new
schema was written; this task only measures the delta.

- **Harness** — one jest spec driving the REAL edge (interceptor +
  decorator mounted, kill-switches at production defaults), not the
  schema in isolation.
- **Probes** — every binding × payload classes: valid; missing-required;
  explicit-null (nullable vs notNull); empty-object; unknown-keys;
  empty-string; numeric-as-string; boolean-as-string; float-for-int;
  overlength; date-forms. Full cross-product, no sampling.
- **Verdicts** — classified against OLD behavior, recovered from git
  history of the old DTO/mapper/service (what actually accepted,
  coerced, dropped, or 500'd) — never assumed from names or comments.
- **Pins** — totals and per-class verdicts pinned hard in the spec, so
  any later schema change flips the audit loudly instead of drifting.
- **Zero edits** — the audit task edits nothing written by the pre-cut
  tasks; it measures and reports, it does not repair.

## Disposition classes

| Class | Meaning | Default action |
|---|---|---|
| parity | old and new agree on accept/reject | record and pin |
| style-divergence | same outcome via a different route (old coerced, new rejects and callers normalize) | sanction — accept the new style |
| error-shift | old 500 mid-transaction → new 400 at the edge | usually sanction — earlier, cheaper failure |
| capability-loss | the old behavior was the ONLY way to do something; the new schema makes it impossible | candidate widen — schema change, human decides |

## The decision file

`docs/<topic>-audit.md`: per-module tables, one row per binding ×
payload class, carrying probe evidence, old-behavior citation, verdict
class, and a one-line human decision slot. The audit task fills
evidence and proposed class; decision slots stay empty. No test edits.

## Human ratification

Per slot the question is binary: **widen** (loosen the new schema to
restore the old capability) or **sanction** (accept the stricter new
behavior). Post-ruling, an implementation task flips the harness pins
to the ratified verdicts and updates the gate manifest. Unratified
capability-loss rows block the merge gate.

## Reference case

drizzle-migration T26: 336 probes across 33 bindings. The highest-risk
finding was a capability loss (null-clear via PATCH impossible under
the new schema), caught ONLY because old behavior was traced through
git history rather than assumed. Counter-lesson: a `z.unknown()` field
that LOOKED like a partial-delta channel wasn't one — the old comment
overstated it; doc-fix only, no code change.

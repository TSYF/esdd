# Design: <SLUG>

- **Date**: <DATE>
- **Status**: drafting

## Design Purpose
<!-- ADD Step 1: why does this system/change exist, and what quality
     outcomes must the architecture serve? Two sentences max. -->

## Iteration Goals Log
<!-- One line per ADD iteration:
     - it-1: establish containers and primary flows for <goal> -->

## Architectural Overview
<!-- Narrative of the chosen structures. Cite an ADR for every significant
     choice (format: ADR-NNNN-slug). If no ADR exists yet, create it with
     `esdd adr new --level spec --title "..."` before finalizing this section. -->

## C4 Views
<!-- System Context and Container views usually live in the SHARED
     .esdd/design.md. Reference them; only duplicate here if this spec
     changes them. Component and Code views are spec-local: -->
- Component: `diagrams/3-component-<name>.puml`
- Code: `diagrams/4-code-<name>.puml`

## Dynamic Views
<!-- Sequence / activity / state machine diagrams for the critical flows. -->
- `diagrams/5-sequence-<name>.puml`

## Data Model
<!-- ER diagram with crow's-foot notation where persistence is involved. -->
- `diagrams/6-er-<name>.puml`

## Interfaces
<!-- "A boundary across which elements meet and interact, communicate, and
     coordinate" - contractual: how information flows, what may depend on it.
     Every interface here MUST be referenced by the tasks that touch it. -->
### `<InterfaceName>`
- **Contract**: signatures / message shapes / invariants
- **Provider**: element producing it
- **Consumers**: elements depending on it
- **Failure modes**: what the consumer sees when it breaks

## Task Relationship Matrix
<!-- Generated; do not hand-edit:
     esdd matrix --spec <SLUG> --out matrix.md -->

## ATAM Evaluation
<!-- Filled in Phase 5. -->
### Scenario Walkthrough Results
### Risks
### Non-risks
### Sensitivities
### Tradeoffs
### Risk Themes

# Utility Tree & Drivers: <SLUG>

## Architectural Drivers (QAW output)

### Business Goals
<!-- e.g. "Reduce signup drop-off from 40% to 10% this quarter." -->

### Constraints
<!-- Hard limits discovered in grilling: legal, budget, tech mandated. -->

### Technical Context
<!-- What exists already that this spec must fit into. -->

## Architecturally Significant Requirements (ASRs)

| ID | ASR | Stimulus | Response (seed) | Measure (seed) |
|----|-----|----------|-----------------|----------------|
| ASR-1 | | | | |

<!-- An ASR is a requirement with architectural impact. Not every
     requirement is an ASR - only ones where the wrong architecture makes
     the requirement expensive or impossible to meet later. -->

## Utility Tree

```
                    <SYSTEM>
        ┌───────────┼────────────┐
   Quality Attr A   Quality Attr B
        │                │
   QAS-A1 (BV,TR)  QAS-B1 (BV,TR)
```

(BV = business value H/M/L, TR = technical risk H/M/L - validated with the human)

## Quality Attribute Scenarios (QAS)

### QAS-1: <short name>
- **Source**: who/what generates the stimulus
- **Stimulus**: the condition arriving at the system
- **Artifact**: what part of the system is stimulated
- **Environment**: normal / peak / startup / degraded / ...
- **Response**: the observable behaviour required
- **Response Measure**: how we know the response succeeded (numbers!)
- **ASR**: links to ASR-n
- **Ranking**: BV = H/M/L, TR = H/M/L

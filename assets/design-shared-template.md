# <WORKSPACE> - Shared Architecture

This workspace uses [ESDD](https://example.invalid/esdd) (Exhaustive
Spec-Driven Development). Global ADRs: `~/.esdd/adrs/`. Directory ADRs:
`.esdd/adrs/`. Specs: `.esdd/specs/<slug>/`. Tasks: `esdd tw -- next`.

## C4 Level 1 - System Context

<!-- Render from: specs' diagrams/1-context-*.puml or paste inline source. -->

```plantuml
' !include specs/_shared/1-context.puml
```

## C4 Level 2 - Containers

<!-- One Container diagram per deployable system in this workspace. -->

```plantuml
' !include specs/_shared/2-container-<system>.puml
```

## Cross-Spec Interfaces
<!-- Interfaces shared by two or more specs live HERE, not in a spec. -->

| Interface | Provider | Consumers | Contract ref |
|-----------|----------|-----------|--------------|

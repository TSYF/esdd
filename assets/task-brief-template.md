# Task brief (stored as the FIRST annotation of every actionable task)

Goal: <one sentence - what exists when this is done that didn't before>
Story: <US-n + the GWT scenario this ticket implements, from
        .esdd/specs/<slug>/proposal.md - the ticket's Testable anchor>
Context: <pointers: design.md sections, ADRs, QAS - not full text>
Touch: <the touches UDA value - file globs this task reads/writes>
Interface obligations: <which .esdd interfaces this task must honour>
Steps:
1. <ordered, concrete>
2. <...>
Verify: <command or test that proves done>
Done when: <the Then of the GWT above - observable without reading source>

<!-- Keep the whole brief under ~600 tokens. Detail lives in design.md;
     the brief points at it. A bloated brief blows the token budget it
     exists to protect. A ticket that cannot name its Story/GWT goes
     back to proposal.md - see references/invest.md rule 6. -->

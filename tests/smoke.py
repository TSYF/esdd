#!/usr/bin/env python3
"""Smoke harness for the esdd CLI. Run: python3 tests/smoke.py"""
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the repo free of __pycache__

ESDD = str(Path(__file__).resolve().parent.parent / "scripts" / "esdd")
WS = Path("/tmp/opencode/esdd-test")
PASS, FAIL = 0, 0


def run(*args, check=True, home=None):
    env = dict(os.environ)
    if home:
        env["HOME"] = home
    r = subprocess.run([sys.executable, ESDD, *args], cwd=WS, env=env,
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"  !! esdd {' '.join(args)} exited {r.returncode}\n{r.stdout}\n{r.stderr}")
    return r


def ok(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} {extra}")


def export():
    r = run("tw", "--", "project:esdd-test.core.rate-limit", "export")
    return {t["description"]: t for t in json.loads(r.stdout)}


print("== sandbox bootstrap (idempotent: wipes and recreates) ==")
subprocess.run(["rm", "-rf", str(WS), "/tmp/opencode/fakehome"], check=True)
(WS).mkdir(parents=True)
Path("/tmp/opencode/fakehome").mkdir(parents=True)
r = run("init", "--graph-nav", "groma", home="/tmp/opencode/fakehome")
ok("init", r.returncode == 0)
r = run("spec", "new", "rate-limit", "--project", "core",
        home="/tmp/opencode/fakehome")
ok("spec new", r.returncode == 0)
for title in ("Token bucket", "Redis store"):
    r = run("adr", "new", "--level", "spec", "--spec", "rate-limit",
            "--title", title, home="/tmp/opencode/fakehome")
    ok(f"adr new spec '{title}'", r.returncode == 0)
r = run("adr", "new", "--level", "global", "--title", "Errors not exceptions",
        home="/tmp/opencode/fakehome")
ok("adr new global", r.returncode == 0)
# every subsequent run() must see the fake HOME (set once here)
os.environ["HOME"] = "/tmp/opencode/fakehome"

print("== tasks: bulk import ==")
tasks = [
    {"description": "Design bucket interface",
     "project": "esdd-test.core.rate-limit", "touches": "src/rate-limit/bucket.ts"},
    {"description": "Implement token bucket",
     "project": "esdd-test.core.rate-limit",
     "touches": "src/rate-limit/bucket.ts,src/rate-limit/token-bucket.ts"},
    {"description": "Redis store adapter",
     "project": "esdd-test.core.rate-limit", "touches": "src/rate-limit/redis-store.ts"},
    {"description": "Wire rate-limit middleware",
     "project": "esdd-test.core.rate-limit", "touches": "src/rate-limit/middleware.ts"},
    {"description": "Run load test on staging", "worker": "human",
     "token_estimate": 5000, "project": "esdd-test.core.rate-limit"},
]
(WS / "tmp-import.json").write_text(json.dumps(tasks))
r = run("tw", "--", "import", str(WS / "tmp-import.json"))
ok("import 5 tasks", r.returncode == 0, r.stderr[-300:])

print("== tasks: blocking edges ==")
by_desc = export()
pairs = [("Implement token bucket", "Design bucket interface"),
         ("Redis store adapter", "Design bucket interface"),
         ("Wire rate-limit middleware", "Implement token bucket"),
         ("Wire rate-limit middleware", "Redis store adapter")]
for child, parent in pairs:
    r = run("tw", "--", by_desc[child]["uuid"], "modify",
            f"depends:{by_desc[parent]['uuid']}")
    ok(f"edge {child} <- {parent}", r.returncode == 0)

print("== matrix ==")
r = run("matrix", "--spec", "rate-limit")
ok("matrix lists 6 tasks", r.stdout.count("\n| ") == 6, r.stdout)
ok("matrix shows dependency", "Design bucket interface" in r.stdout)
_loader = importlib.machinery.SourceFileLoader("esdd_cli", ESDD)
_spec = importlib.util.spec_from_loader("esdd_cli", _loader)
_esdd = importlib.util.module_from_spec(_spec)
_loader.exec_module(_esdd)
cyc = _esdd.find_cycles({"a": ["b"], "b": ["c"], "c": ["a"], "d": []})
ok("find_cycles detects loop", len(cyc) == 1 and set(cyc[0]) == {"a", "b", "c"})
ok("find_cycles ignores dags", _esdd.find_cycles({"a": ["b"], "b": ["c"], "c": []}) == [])

print("== estimate ==")
(WS / "src/rate-limit").mkdir(parents=True, exist_ok=True)
for f, size in [("bucket.ts", 20000), ("token-bucket.ts", 30000),
                ("redis-store.ts", 10000), ("middleware.ts", 8000)]:
    (WS / "src/rate-limit" / f).write_text("x" * size)
r = run("estimate", "--spec", "rate-limit", "--set")
ok("estimate ran", "Est. tokens" in r.stdout, r.stdout)
by_desc = export()
impl = by_desc["Implement token bucket"]
est = impl.get("token_estimate")
expect = (20000 + 30000) // 4 + 1500 * 2
ok("estimate math + persisted", est == expect, f"est={est} expect={expect}")
r = run("estimate", "--spec", "rate-limit")
ok("ok verdicts", " ok " in r.stdout, r.stdout)

print("== review gates ==")
review_proposal = """# Proposal: rate limit

## User Stories

| ID | Story |
|----|-------|
| US-1 | As an API client, I want limits so that abuse is bounded. |

### Acceptance Scenarios (Given/When/Then)

**US-1**
```gherkin
Given a client over the configured limit
When the client calls the endpoint
Then it receives HTTP 429 with Retry-After
```

## Impact Map

| Goal (Why) | Actor (Who) | Impact (How) | Deliverable (What) |
|------------|-------------|--------------|--------------------|
| Bound abuse | API client | gets 429 over limit | US-1 |
"""
(WS / ".esdd/specs/rate-limit/proposal.md").write_text(review_proposal)
(WS / ".esdd/specs/rate-limit/design.md").write_text("""# Design: rate-limit

## Interfaces

### `BucketStore`
- **Contract**: take(key, cost) -> Decision
- **Provider**: rate-limit middleware
- **Consumers**: route handlers
- **Failure modes**: fails closed with 503
""")

briefs = {
    "Design bucket interface": (
        "Goal: pin the bucket contract\nStory: US-1\n"
        "Context: design.md Interfaces\nTouch: src/rate-limit/bucket.ts\n"
        "Interface obligations: `BucketStore`\nSteps:\n1. write the contract\n"
        "Verify: npx vitest run src/rate-limit/bucket.test.ts\n"
        "Done when: HTTP 429 with Retry-After is observable"),
    "Implement token bucket": (
        "Goal: implement the bucket\nStory: US-1\n"
        "Context: design.md Interfaces\n"
        "Touch: src/rate-limit/bucket.ts,src/rate-limit/token-bucket.ts\n"
        "Interface obligations: `BucketStore`\nSteps:\n1. code it\n"
        "Verify: npx vitest run src/rate-limit/token-bucket.test.ts\n"
        "Done when: HTTP 429 with Retry-After is observable"),
    "Redis store adapter": (
        "Goal: shared counter store\nStory: US-1\n"
        "Context: design.md Interfaces\nTouch: src/rate-limit/redis-store.ts\n"
        "Interface obligations: `BucketStore`\nSteps:\n1. add the adapter\n"
        "Verify: npx vitest run src/rate-limit/redis-store.test.ts\n"
        "Done when: HTTP 429 with Retry-After is observable"),
    "Wire rate-limit middleware": (
        "Goal: enforce limits per endpoint\nStory: US-1\n"
        "Context: design.md Interfaces\nTouch: src/rate-limit/middleware.ts\n"
        "Interface obligations: `BucketStore`\nSteps:\n1. wire it\n"
        "Verify: npx vitest run src/rate-limit/middleware.test.ts\n"
        "Done when: HTTP 429 with Retry-After is observable"),
    "Run load test on staging": (
        "Goal: prove the p99 budget\nStory: US-1\nContext: proposal.md\n"
        "Touch: none\nInterface obligations: none\nSteps:\n1. run the soak\n"
        "Verify: echo load-test-ok\n"
        "Done when: p99 delta is at most 5ms"),
}
by_desc = export()
for desc, brief in briefs.items():
    t = by_desc[desc]
    r = run("tw", "--", t["uuid"], "annotate", brief)
    ok(f"brief added: {desc}", r.returncode == 0, r.stderr[-120:])
    if t.get("worker") != "human":
        run("tw", "--", t["uuid"], "modify", "worker:agent")

r = run("review", "--gate", "tickets", "--spec", "rate-limit", "--json",
        check=False)
ok("review tickets passes on demo spec",
   r.returncode == 0 and json.loads(r.stdout)["pass"] is True, r.stdout[-500:])
report = WS / ".esdd/specs/rate-limit/review-tickets.md"
ok("review writes review-tickets.md", report.is_file())
ok("report has the checks matrix", report.is_file() and
   "## Checks" in report.read_text() and "| rule | status | detail |" in report.read_text())
try:
    state = json.loads((WS / ".esdd/state.json").read_text())
    gate = state.get("gates", {}).get("tickets", {})
    ok("review stamps gates.tickets.last_run",
       isinstance(gate.get("last_run"), str) and len(gate["last_run"]) == 10,
       str(gate))
except json.JSONDecodeError:
    ok("review stamps gates.tickets.last_run", False, "state.json unreadable")

r = run("tw", "--", "add", "Broken review ticket",
        "project:esdd-test.core.rate-limit",
        "touches:src/rate-limit/bucket.ts",
        "token_estimate:5000", "worker:agent")
ok("plant a broken review ticket", r.returncode == 0)
by_desc = export()
bogus = by_desc["Broken review ticket"]
run("tw", "--", bogus["uuid"], "annotate",
    "Goal: broken brief\nContext: none\nSteps:\n1. do nothing")
r = run("review", "--gate", "tickets", "--spec", "rate-limit", "--json",
        check=False)
rev = json.loads(r.stdout)
rules = {v["rule"] for v in rev["violations"]}
ok("review tickets fails planted brief",
   r.returncode == 1 and rev["pass"] is False, r.stdout[-400:])
ok("planted brief hits brief-story", "brief-story" in rules, str(rules))
ok("planted brief hits brief-verify", "brief-verify" in rules, str(rules))
ok("round 2 records new violations",
   rev["rounds"][-1]["round"] == 2 and rev["rounds"][-1]["new"] >= 3,
   str(rev["rounds"][-1]))

r = run("review", "--gate", "tickets", "--spec", "rate-limit", "--json",
        check=False)
rev = json.loads(r.stdout)
ok("second round escalates the same violation",
   r.returncode == 1 and any(v.get("escalate") for v in rev["violations"]),
   str(rev["violations"]))
ok("round 3 records unfixed violations",
   rev["rounds"][-1]["round"] == 3 and rev["rounds"][-1]["unfixed"] >= 3,
   str(rev["rounds"][-1]))
ok("report surfaces escalate-to-human",
   "Escalate to human" in report.read_text())

run("tw", "--batch", "--", bogus["uuid"], "delete")
r = run("review", "--gate", "tickets", "--spec", "rate-limit", "--json",
        check=False)
rev = json.loads(r.stdout)
ok("review passes after the fix",
   r.returncode == 0 and rev["pass"] is True, r.stdout[-400:])
ok("round 4 records fixed violations",
   rev["rounds"][-1]["round"] == 4 and rev["rounds"][-1]["fixed"] >= 3,
   str(rev["rounds"][-1]))

run("spec", "new", "placeholder", "--no-index")
r = run("review", "--gate", "design", "--spec", "placeholder", "--json",
        check=False)
rev = json.loads(r.stdout)
ok("design gate passes on a placeholder spec",
   r.returncode == 0 and rev["pass"] is True, r.stdout[-400:])
ok("design gate emits judgment rows",
   any(c["status"] == "judgment" for c in rev["checks"]), str(rev["checks"]))

r = run("review", "--gate", "code", "--spec", "rate-limit", check=False)
ok("code gate requires --task", r.returncode == 2 and "--task" in r.stderr,
   f"rc={r.returncode} {r.stderr[-120:]}")
impl = by_desc["Implement token bucket"]
r = run("review", "--gate", "code", "--spec", "rate-limit",
        "--task", impl["uuid"], "--json", check=False)
rev = json.loads(r.stdout)
ok("code gate passes with a brief",
   r.returncode == 0 and rev["pass"] is True, r.stdout[-400:])
ok("code gate emits judgment rows",
   any(c["status"] == "judgment" for c in rev["checks"]), str(rev["checks"]))

print("== phase ==")
r = run("phase", "add", "--spec", "rate-limit")
ok("phase add with placeholder prereqs", r.returncode == 0)
(WS / ".esdd/specs/rate-limit/utility-tree.md").write_text("# Utility Tree\n\n" + "filled " * 60)
(WS / ".esdd/specs/rate-limit/proposal.md").write_text("# Proposal\n\n" + "filled " * 60)
r = run("phase", "add", "--spec", "rate-limit", "--done")
ok("phase add --done", "marked done" in r.stdout, r.stdout)
r = run("phase")
ok("phase state readable", "add" in r.stdout, r.stdout)

print("== verify ==")
idx = by_desc["rate-limit :: spec index"]
run("tw", "--", idx["uuid"], "modify", 'adrs:"0099-nonexistent"')
r = run("verify", "--spec", "rate-limit", check=False)
ok("fails on bogus adrs entry", r.returncode == 1 and "do not exist" in r.stdout,
   r.stdout)
run("tw", "--", idx["uuid"], "modify",
    'adrs:"0001-token-bucket,0002-redis-store"')
(WS / ".esdd/specs/rate-limit/adrs/0001-token-bucket.md").write_text(
    "# 0001. Token bucket\n\n## Status\nproposed\n")
(WS / ".esdd/specs/rate-limit/adrs/0002-redis-store.md").write_text(
    "# 0002. Redis store\n\n## Status\nproposed\n")
r = run("verify", "--spec", "rate-limit", check=False)
ok("passes with synced adrs", r.returncode == 0, r.stdout)

wire = by_desc["Wire rate-limit middleware"]
run("tw", "--", wire["uuid"], "modify", "token_estimate:200000")
r = run("verify", "--spec", "rate-limit", check=False)
ok("fails over hard limit", r.returncode == 1 and "hard limit" in r.stdout, r.stdout)
run("tw", "--", wire["uuid"], "annotate", "HARDCAP-APPROVED: human accepted")
r = run("verify", "--spec", "rate-limit", check=False)
ok("hard cap with sign-off passes", r.returncode == 0, r.stdout)
run("tw", "--", wire["uuid"], "modify", "token_estimate:5000")
r = run("verify", "--spec", "rate-limit", check=False)
ok("prints human work order", r.returncode == 0 and
   "Run load test on staging" in r.stdout, r.stdout)

print("== graph import / retro ==")
snap = {
    "elements": [
        {"id": "person-customer", "name": "Customer", "kind": "person",
         "description": "buys things"},
        {"id": "svc-shop", "name": "shop", "kind": "container",
         "tech": "Node", "path": "services/shop/**"},
        {"id": "db-orders", "name": "orders", "kind": "datastore",
         "tech": "Postgres", "path": "db/**"},
        {"id": "sys-psp", "name": "Payment provider", "kind": "system"},
    ],
    "edges": [
        {"src": "person-customer", "dst": "svc-shop", "type": "uses"},
        {"src": "svc-shop", "dst": "db-orders", "type": "reads-writes"},
        {"src": "svc-shop", "dst": "sys-psp", "type": "charges"},
    ],
    "meta": {"source": "groma", "captured": "2026-11-05", "repo": "esdd-test"},
}
(WS / "snap-test.json").write_text(json.dumps(snap))
r = run("import", "--source", "groma", "--path", str(WS / "snap-test.json"),
        "--snapshot")
ok("import groma snapshot", r.returncode == 0 and "4 elements, 3 edges" in r.stdout,
   r.stdout + r.stderr)
r = run("import", "--source", "groma", "--path", str(WS / "snap-test.json"),
        "--snapshot", "--notes", "smoke test")
ok("import idempotent + notes", r.returncode == 0 and "4 elements" in r.stdout)
(WS / ".esdd/graph/bogus").mkdir(parents=True, exist_ok=True)
(WS / ".esdd/graph/bogus/snapshot.json").write_text('{"elements": "oops"}')
r = run("import", "--source", "bogus")
ok("invalid snapshot flagged", "not a valid normalized snapshot" in r.stdout,
   r.stdout)
r = run("import", "--list-sources")
ok("list-sources shows both", "groma" in r.stdout and "bogus" in r.stdout,
   r.stdout)
ok("list-sources shows edge counts", "elements," in r.stdout, r.stdout)
r = run("import")
ok("import without source errors", r.returncode == 1)
r = run("import", "--source", "Bad.Source")
ok("import slug validation", r.returncode == 1 and "no dots" in r.stderr)

print("== new CLI surface (specialist rollout) ==")
r = run("phase", "qaw", "--spec", "nope-strict", "--strict")
ok("phase --strict exits 2 on missing prereq", r.returncode == 2 and
   "missing prerequisites" in r.stderr, f"rc={r.returncode} {r.stderr[-100:]}")
r = run("phase", "product", "--spec", "rate-limit", "--strict")
ok("phase --strict passes when prereqs exist", r.returncode == 0, r.stdout)
r = run("spec", "list", "--json")
try:
    rows = json.loads(r.stdout)
    ok("spec list --json parses", isinstance(rows, list) and
       any(x["spec"] == "rate-limit" for x in rows), r.stdout)
    rl = [x for x in rows if x["spec"] == "rate-limit"][0]
    ok("spec list --json design flag uses D", rl["design"] is True, str(rl))
except json.JSONDecodeError:
    ok("spec list --json parses", False, r.stdout)
r = run("matrix", "--spec", "rate-limit", "--json")
try:
    m = json.loads(r.stdout)
    ok("matrix --json parses", len(m["tasks"]) == 6 and m["cycles"] == [] and
       any(t["depends"] for t in m["tasks"]), r.stdout[:200])
except json.JSONDecodeError:
    ok("matrix --json parses", False, r.stdout)
r = run("estimate", "--touches",
        "src/rate-limit/bucket.ts,src/rate-limit/token-bucket.ts")
ok("estimate --touches (no taskwarrior)", "tokens over 2 files: ok" in r.stdout,
   r.stdout)
r = run("estimate", "--touches", "src/rate-limit/bucket.ts", "--json")
try:
    e = json.loads(r.stdout)
    ok("estimate --touches --json", e["verdict"] == "ok" and e["files"] == 1,
       r.stdout)
except json.JSONDecodeError:
    ok("estimate --touches --json", False, r.stdout)
r = run("verify", "--spec", "rate-limit", "--json")
try:
    v = json.loads(r.stdout)
    ok("verify --json", v["pass"] is True and v["spec"] == "rate-limit" and
       len(v["human_work_order"]) == 1, r.stdout[:200])
except json.JSONDecodeError:
    ok("verify --json", False, r.stdout)
r = run("env", "set", "GRAPH_NAV", "groma")
ok("env set K V documented form", r.returncode == 0 and
   "GRAPH_NAV=groma" in r.stdout, r.stdout + r.stderr)
r = run("env", "set")
ok("env set without value errors", r.returncode == 1 and "usage" in r.stderr)
(WS / "jira-123.md").write_text("# JIRA-123: rate limit\n\nAcceptance: user gets 429 over limit\n")
r = run("po", "import", str(WS / "jira-123.md"), "--spec", "rate-limit")
ok("po import copies to sources/", r.returncode == 0 and
   (WS / ".esdd/specs/rate-limit/sources/jira-123.md").is_file(),
   r.stdout + r.stderr)
r = run("po", "import", str(WS / "jira-123.md"), check=False)
ok("po import requires --spec", r.returncode == 2 and "--spec" in r.stderr,
   f"rc={r.returncode} {r.stderr[-80:]}")

print("== retro phase (workspace level) ==")
r = run("phase", "retro")
ok("retro has no spec prerequisite",
   r.returncode == 0 and "workspace level" in r.stdout, r.stdout)
ok("retro points at reference doc", "references/retro.md" in r.stdout, r.stdout)
r = run("phase", "retro", "--done")
ok("retro --done", "marked done" in r.stdout, r.stdout)
r = run("phase")
ok("retro recorded without active spec", "retro" in r.stdout, r.stdout)
r = run("phase", "retro", "--spec", "some-spec")
ok("retro ignores --spec gracefully", r.returncode == 0, r.stdout)

print("== adr list aggregation ==")
r = run("adr", "list")
ok("adr list shows all levels", "[spec:rate-limit]" in r.stdout and
   "[global]" in r.stdout, r.stdout)

print("== doctor ==")
r = run("doctor", home="/tmp/opencode/fakehome")
ok("doctor reports", "workspace root" in r.stdout and "GRAPH_NAV" in r.stdout)
ok("doctor shows graph sources", "graph sources:" in r.stdout and
   "groma" in r.stdout, r.stdout)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)

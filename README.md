# astack

Reusable agent workflows with project-owned rules, immutable snapshots, drift checks,
isolated upstream preparation, and reversible adoption. Python 3.11+ and Git are
enough for the core CLI. No agent subscription is required for contributor checks.

## Use

Run `bin/workflow --help` from this source, or install the CLI with
`python3 -m pip install .`. Run `make check` to verify the source.

1. Copy `examples/workflow.json` to the project's root as `workflow.json`. Select a
   profile and the full Git commit of this source. Keep the project's real checks and
   required documents. `null` means a check is unavailable; it never means passed.
2. Copy `examples/host.json` to a private local path. Map any project identifiers to
   their checkouts, list capability probe argument arrays and global discovery roots.
   Include each actual provider/plugin skill discovery root to detect duplicates.
   Drain existing sessions before setting that checkout's `drained` field to true.
3. Preview, prepare and verify:

   ```sh
   bin/workflow --host /private/host.json bootstrap --project example --source . --dry-run
   bin/workflow --host /private/host.json bootstrap --project example --source .
   bin/workflow --host /private/host.json doctor --project example --json
   bin/workflow --host /private/host.json run --project example -- your-agent
   ```

Commit `workflow.json`, `.workflow-managed.json`, `.agents/skills/`, optional Claude
aliases/copies, and `tools/workflow.py` in the consuming project. The vendored CLI
runs independently: `python3 tools/workflow.py doctor --project . --json`.
Use `--host` for host capabilities and global discovery verification. Without it,
doctor verifies only the checkout and has no evidence for host-specific capabilities.
Use `--state` before the command to select another private host state root.
The optional `locks` map references the manager-owned skills lock and the generated
tools lock. With a tools lock selected, bootstrap also vendors `tools/upstream.py`
and the approved `tools.lock.json`; run `python3 tools/upstream.py --lock tools.lock.json`
for the same upstream preparation commands. Generated manifests are never hand-edited.

## Update and rollback

```sh
bin/workflow --host /private/host.json update --project example --source . --candidate FULL_COMMIT
# Review the candidate JSON in the printed local path; exercise it in a disposable clone.
bin/workflow --host /private/host.json bootstrap --project example --candidate FULL_COMMIT --dry-run
bin/workflow --host /private/host.json bootstrap --project example --candidate FULL_COMMIT
bin/workflow --host /private/host.json rollback --project example --to PREVIOUS_FULL_COMMIT
```

Updates only stage; bootstrap activates after drift, collision and drain checks.
Bootstrap twice does not rewrite verified content. A managed edit stops with a diff
when the local baseline is available. Existing unowned skills are never adopted by
matching names. Reconcile them in a proposal checkout first. Rollback restores owned
entries and the previous descriptor; unrelated project files and settings survive.

Managed sessions hold a durable lease for their whole child process. If a launcher
is killed, inspect the private session record and terminate any surviving child
before `session-close --project example --token TOKEN`. Leases never expire silently.
An interrupted activation blocks doctor/run; the next bootstrap recovers the journal.
A conflicting edit after interruption stops recovery for manual reconciliation.
Direct agent launches bypass these protections. The local drain declaration covers
those existing sessions; it is an operator assertion, not automatic detection.

## Upstream tools

`tools.lock.json` owns gstack and the skills CLI release, not project skill entries.
Never hand-edit a manager-owned `skills-lock.json`.

```sh
python3 -m astack.upstream --lock tools.lock.json gstack-prepare --adapter codex --target /private/astack/gstack-generation-1
python3 -m astack.upstream --lock tools.lock.json gstack-verify --target /private/astack/gstack-generation-1
python3 -m astack.upstream --lock tools.lock.json skills-restore --target /private/astack/empty-candidate --skills-lock /project/skills-lock.json
```

Gstack preparation runs stock upstream setup, prefixes its commands, isolates both
provider roots and state, and disables both automatic upgrades and update checks.
It does not activate or modify a global installation. The returned record includes
the environment variables needed to launch a fresh agent against that generation.
Keep those variables set for the complete agent process. Verify the generation before
launch; add that verification command as a required host capability when adopting it.
Do not point an existing session at a new generation. Chromium installation and
live browser proof are separate pending capabilities; setup builds the helper only.
Codex's gstack integration is experimental upstream. Core skills choose no model.

The skills CLI restores only into a nonexistent candidate directory, with force and
frozen-lock flags. Its ordinary restore accepts existing directories without checking
bytes, so do not use it alone as a drift check. Historical locks lacking sufficient
source identity can fail frozen restoration; do not silently resolve latest or amend
the lock to hide this. Keep such migrations pending until a restorable lock is produced
by the manager. See [feasibility evidence](docs/feasibility.md).

## Rollout and boundaries

See [design decisions](docs/design.md), [verification](docs/verification.md), and the
private rollout record under `.local/`. The local original plan is ignored because
it contains host/project inventory. Publication visibility is not decided here.

Core mechanics are tested on the local macOS host. The CI matrix is configured for
Linux/macOS and Python 3.11/3.13; a configured job is not evidence it has run. Actual
agent discovery, native journeys, remote adoption and external-project governance
remain separate evidence gates. No hooks, global settings, credentials, production
configuration or deployment actions are part of bootstrap.

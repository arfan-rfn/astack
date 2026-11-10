# astack

Shared agent skills with pinned snapshots, drift checks and reversible updates.
Python 3.11+ and Git are enough for the core CLI; it has no runtime dependencies.

## Start

Run `make check` to test the source. Use `bin/workflow` directly or install with
`python3 -m pip install .`.

Copy [workflow.json](examples/workflow.json) into your project. Use the `core` profile
and a full astack Git commit. Keep project commands and required documents there;
`null` means a check is unavailable. Copy [host.json](examples/host.json) to a private
location and map your checkout, capability probes and actual discovery roots.
Drain existing sessions before declaring that checkout `drained`.

```sh
bin/workflow --host /private/host.json bootstrap --project example --source . --dry-run
bin/workflow --host /private/host.json bootstrap --project example --source .
bin/workflow --host /private/host.json doctor --project example --json
bin/workflow --host /private/host.json run --project example -- your-agent
```

Commit the generated descriptor, manifest, `.agents/skills`, Claude aliases/copies,
and `tools` files in the consuming project. Its CLI runs independently:
`python3 tools/workflow.py doctor --project . --json`. Supply `--host` for host
capabilities and global discovery checks. Use `--state` to choose private state storage.

## Update and recover

```sh
bin/workflow --host /private/host.json update --project example --source . --candidate FULL_COMMIT
bin/workflow --host /private/host.json bootstrap --project example --candidate FULL_COMMIT --dry-run
bin/workflow --host /private/host.json bootstrap --project example --candidate FULL_COMMIT
bin/workflow --host /private/host.json rollback --project example --to PREVIOUS_FULL_COMMIT
```

Update stages a candidate; bootstrap activates after drift and drain checks. To change
project configuration, add `--descriptor proposal.json` to update. Managed edits and
unowned collisions stop installation. Rollback preserves unrelated files and settings.

Use `run` to hold a session lease. Direct launches bypass it and require an operator
drain. After a killed launcher, inspect surviving work before explicitly closing its
lease with `session-close --project example --token TOKEN`. Interrupted activation
blocks new sessions until bootstrap recovers its journal; conflicting edits stop recovery.

## Upstream tools

`tools.lock.json` pins gstack and the skills CLI. The skills manager owns
`skills-lock.json`. Selecting a tools lock also vendors `tools/upstream.py` for
standalone use; from this source run:

```sh
python3 -m astack.upstream --help
```

Gstack uses stock setup in separate provider/state roots with automatic updates off.
Launch a fresh agent with the prepared record's environment and verify that generation
before use. Skills restore only into empty candidates with frozen locks. Browser/native
capabilities need separate proof. See [feasibility and limitations](docs/feasibility.md).

Keep one core profile until different behavior warrants another. Project rules stay
with projects. [Design decisions](docs/design.md) explain recovery and scope;
[verification](docs/verification.md) records tests and pending rollout gates.
Private pilot evidence lives under the ignored `.local/` directory. It is not published.

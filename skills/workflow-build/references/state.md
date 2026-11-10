# Build state and worker briefs

Use one durable record per plan, for example `plan/<slug>-build-state.md`, unless
project policy selects another location. It is the orchestrator's memory across
restarts. The orchestrator alone updates it; workers return handoffs. Keep credentials
and private account data out. Write before starting an operation and after it ends;
use observed ISO 8601 timestamps with an explicit timezone.
Record task and checkpoint transitions concisely; link bulky logs instead of copying
them into the ledger. Uncommitted work needs HEAD plus a diff or content identity,
not HEAD alone, to identify the inputs that were verified.

## Record layout

Keep these sections in the record; add rows as actual tasks are discovered.

- **Current:** plan path, selected/deferred releases, repositories and revisions,
  workflow source revision when known, current checkpoint, next action, updated time.
- **Releases:** dependencies, acceptance journeys, task coverage, checkpoint status,
  integrated revisions, evidence, and unverified prerequisites.
- **Tasks:** the ledger below, plus each task's saved worker brief.
- **Decisions and amendments:** user changes, shared contract changes, rationale,
  affected tasks/workers, and unresolved questions.
- **Approvals:** each approval and pre-approval the user gave, with its exact scope
  and time, and the questions still waiting for the user.
- **Events and handoffs:** starts, completions, worker reports, review findings,
  correction rounds, integration attempts, and observed failures with timestamps.
- **Verification and final handoff:** commands, working directories, exit statuses,
  consumed revisions, evidence paths, blockers, manual checks, and review/ship next steps.

Use this task ledger; workspace and runtime details can live in the saved brief when
rows become too wide.

| Task | Release / outcome | Depends on | Allowed files / workspace | Worker / tool / runtime | Status | Checks / revision / evidence | Updated at |
|---|---|---|---|---|---|---|---|

Statuses: `pending` -> `running` -> `review` -> `integrated`. Use `blocked` for an
unresolved prerequisite or failed integration, recording the prior state and next
action. A correction returns the task to `running` under one active owner. Mark work
`deferred` only when the plan or user defers it. Record worker completion separately
from review acceptance, integration, and release acceptance.

## Worker brief

Give each worker the relevant context, not the whole conversation:

- Task ID, selected release, one concrete outcome, and acceptance conditions.
- Repository/workspace and base revision; dependency results and shared contracts.
- Project instructions, allowed files, explicit exclusions, and resource isolation.
- Required checks and any infrastructure/provider prerequisites.
- Approved public test seams and TDD red/green evidence for behavior changes.
- Build-state record location for context; return results to the orchestrator.
- Boundaries: own task only, no nested delegation, no unrelated edits or publishing.

The worker handoff names its task ID, changed files and commit/diff location, commands
actually run with results, remaining failures or blockers, and interface assumptions.
A worker finding work outside its brief reports it rather than silently expanding scope.

## Restart and stale evidence

Compare the record with Git, actual workspaces, and available completion information.
Follow the host's continuation rules for running workers; do not start duplicate owners.
Check partial integration before retrying it. If a recorded worker no longer exists,
recover its files/diff and assign only the remaining work after confirming it stopped.

Record discrepancies, then resume the first unverified task or release checkpoint.
Do not trust an old green result after its inputs change, or redo verified work
unchanged. If CI fails after a green checkpoint, reopen the affected release and
its dependents, preserve the failure, and rerun relevant checks on the corrected revision.

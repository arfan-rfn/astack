---
name: workflow-build
description: Build or resume an approved plan with one orchestrator, small parallel worker tasks, and a persistent record of assignments, integration, and acceptance evidence.
---

# Orchestrated build session

The main agent is the orchestrator. Delegate bounded implementation tasks to workers;
keep scope, shared contracts, scheduling, reviews, integration, and saved state with
the orchestrator. Run independent tasks in parallel within the available worker limit.
Small tasks do not imply a smaller or different model: honor user/project choices,
record actual runtime settings, and never silently substitute a provider.
Mark settings the host does not expose as unknown rather than guessing them.

Use supported subagent/delegation tools and follow the host's rules for background
work, isolation, and continuation. Create workers, not unrelated top-level chat
threads. If delegation is unavailable or forbidden, report the missing capability;
do not silently present solo implementation as an orchestrated build.

## Prepare or resume

Read the approved plan and project instructions, architecture, constraints, and check
commands. Apply the project's approval requirements. Build all selected releases;
keep explicitly deferred work separate. Check prerequisites before dependent work.
A missing capability blocks the affected tasks, not independent preparation.

Read [the state record and worker brief](references/state.md) before dispatching.
Use the project's planning directory, or a private local directory when required.
Tell the user the record's location. On restart, read it first and reconcile it with
actual Git revisions, diffs, worker completions, and unfinished integration. Preserve
valid completed work, reopen stale evidence, and resume the first unverified step.
Do not repeat an operation merely because conversation context was lost.

Map releases, acceptance journeys, and dependencies. Split implementation into tasks
with one reviewable outcome, explicit files, shared interfaces, and concrete checks.
A task that spans unrelated outcomes should be split again. Record the task graph
and integration order before starting workers. Define shared contracts first; keep
changes to them with the orchestrator and notify affected workers of amendments.

Use isolated checkouts through supported tools when available. If workers must share
a checkout, give them disjoint file ownership and isolated outputs; only the
orchestrator performs Git mutations. Otherwise serialize conflicting tasks. Follow
project rules for ports, credentials, generated files, and serialized database suites.

## Dispatch and track

For each ready task, save its brief and assignment before dispatch. Give the worker
the relevant plan, contract, project rules, allowed files, checks, workspace, and
handoff requirements from the state reference. Workers implement and test their own
small task; they do not spawn more workers, merge other tasks, push, or deploy.

Start independent tasks together up to the host's capacity. Launch a dependent task
only after its prerequisites pass integration checks. Record each worker's actual ID,
workspace, tool, runtime settings, status, and timestamps. Keep one active owner per
task. While workers run, prepare reviews, acceptance checks, or other unblocked
orchestrator work. Follow completion events and the tool's continuation instructions;
do not busy-poll workers or edit files they own.

When a worker returns, save its handoff and inspect the actual diff and test evidence.
A worker reporting success means ready for review, not complete. Check file ownership,
interfaces, edge cases, and the project's quality bar. Send concrete fixes back to
the owning worker and review the result again. Additional reviewer agents are useful
when risk warrants them; they do not replace the orchestrator's acceptance decision.

Integrate accepted changes in dependency order. Resolve conflicts against the shared
contract and rerun the relevant checks on the combined result. Mark a task integrated
only after these checks pass. A failed integration holds dependent tasks; record the
failure, assign the fix, and rerun verification on the corrected revision.

## Failures and changes

Record failures, blocked work, and user changes as they arrive. Update affected tasks
and acceptance journeys; append amendments to dispatched briefs rather than silently
rewriting what a worker was asked to do. Continue unaffected tasks.

If a worker fails or disappears, inspect its workspace and recorded output before
retrying. Confirm the previous worker has stopped, or cancel it through the supported
tool, before assigning a replacement. Preserve useful work and hand over the remaining
scope and failures. After two unsuccessful correction rounds on the same issue,
reassess the diagnosis and brief; escalate unresolved scope or contract decisions
instead of looping or spawning competing owners.

## Prove and hand off

At each release checkpoint, exercise its acceptance journeys on the combined result,
including cross-component behavior and awkward inputs. Completed worker tasks alone
do not prove a release works. Do not start a release whose required checkpoint is red.
Keep unavailable provider, browser, native, or other required proof visibly pending.

Use project check commands and review/QA procedures, including gstack where required.
Preserve tests and coverage requirements. Record commands, exit statuses, revisions,
and actual results; reopen affected evidence if inputs change or later CI fails.

Finish when the selected scope has integrated changes and current acceptance evidence,
or explicitly report the unresolved tasks and blockers. Save the final state and
handoff: changed revisions, decisions, checks, unfinished work, manual verification,
and the next action. Preserve work needed for review; clean up only owned disposable
resources whose work is safely integrated. Building does not itself authorize paid
calls, real sends, pushes, merges to the default branch, or production deployment.

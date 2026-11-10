# Restart and evidence record

Keep task state in the project's declared planning directory, or a host-local record
when project policy does not permit committing it. Exclude credentials and accounts.

Record:

- Plan path and selected releases; actual source revisions and workflow revision.
- Current step; acceptance journeys; dependencies and responsible lanes, if any.
- Decisions with rationale and rejected alternatives; unresolved questions.
- Each action's timezone-aware start/end timestamp and result.
- Verification command, working directory, exit status, revision and evidence path.
- Blockers, changed prerequisites, deviations, and the next recovery action.

Write before starting an operation and after it finishes. On restart, inspect Git,
worktrees and the current capability results before trusting the record. Mark old
evidence stale if consumed inputs changed. Never repeat an irreversible operation
only because the previous session lost its conversation history.

If CI fails after an earlier green result, reopen the affected release and every
dependent journey. Record the failing revision and rerun the relevant checks after
the fix; do not carry the earlier green verdict into the handoff.

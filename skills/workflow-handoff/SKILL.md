---
name: workflow-handoff
description: Hand off verified work with exact revisions, release boundaries, recovery state and honest exceptions.
---

# Evidence handoff

Read the project descriptor and saved task state. Report what changed, why, the
consumed revisions, checks actually run, and material limitations. Name any reused
checks and their applicable inputs. Do not imply an untested host or adapter passed.

Record each release's readiness separately. List pending CI, unfinished integrated
journeys, optional platform proof, governance decisions and rollout exceptions with
the next action. Preserve the project's normal review/ship/deploy separation.

Before an update, stage a candidate and verify it in a disposable checkout. Activate
only after affected sessions drain. Retain the previous verified release and owned
entry backup, exercise rollback, and record the outcome. Never update a running
session's skill files or roll back unrelated user settings and changes.

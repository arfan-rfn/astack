---
name: workflow-handoff
description: Hand off verified work with exact revisions, release boundaries, recovery state and honest exceptions.
---

# Evidence handoff

Read the project's instructions and saved task state. Report what changed, why, the
consumed revisions, checks actually run, and material limitations. Name any reused
checks and their applicable inputs. Do not imply an untested host or adapter passed.

Record each release's readiness separately. List pending CI, unfinished integrated
journeys, optional platform proof, governance decisions and rollout exceptions with
the next action. Preserve the project's normal review/ship/deploy separation.

When updating shared skills, record the source Git revision and review the diff
before copying files. Preserve local edits and wait for sessions using those files
to finish. Keep the previous version recoverable through Git or a backup. Never
overwrite unrelated project rules or user settings.

---
name: workflow-build
description: Implement an approved project plan, recover interrupted work, and verify each acceptance journey with current evidence.
---

# Build an approved plan

Read the project's instructions, architecture documents, and approved plan. Follow
project rules and preserve its verification commands. Check that the tools and
capabilities needed for each journey are available before starting dependent work.

Read [state and evidence](references/state.md) before changing files. Resume from the
saved state after checking it against Git and the actual environment. A stale green
result is never evidence for a changed revision. Record divergences explicitly.

Map every plan release to an acceptance journey and its dependencies. Implement
dependencies first. Decompose only where interfaces and file ownership are clear.
Use available delegation only when authorized by the user/project and supported by
the active agent. Record actual provider, model, settings, revision and tool; never
silently substitute a provider or enforce a generic model preference.

Preserve constraints, add meaningful regression tests, run the applicable fast/task/
full lanes, and exercise the surface the change serves. Completed component lanes do
not establish that a cross-component journey works. Keep failed or unavailable proof
visible; use deterministic no-provider checks when that is the accepted scope.

Record project-specific commands, service ports, data isolation, and release rules in
project documents. Do not infer permission for paid calls, real sends, production
operations, pushes, or deployments from this skill. Apply the authorized boundary
from the plan and conversation. Follow the project's review and QA workflow,
including gstack where the project uses it.

Finish with a handoff listing changed revisions, commands actually run, results,
unverified journeys, decisions, and the next authorized action. Update saved state
before handing off.

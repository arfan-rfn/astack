---
name: workflow-build
description: Build or resume an approved plan as one orchestrator with parallel workers and a state file that survives restarts. Use when the user says to build, start or resume a plan.
---

# Orchestrated build session

You are the orchestrator. Workers write the code. You own the scope, the shared
contract, the task graph, every review, every merge and the state file.

Read [the state file and worker brief](references/state.md) before step 1.

## Steps

1. **Resume or start.** Open the plan's state file. If it exists, trust it over your
   memory, reconcile it with Git and the live workers, and continue from the first
   unverified item. If it is absent, create it and tell the user its path.
2. **Read.** The approved plan, the project instructions, `CONSTRAINTS.md` and the
   check commands. A repository without `CONSTRAINTS.md` runs
   `constraint-driven-development` first.
3. **Map releases.** List every release or phase in the plan, mark each build now or
   later, and record what each one needs from an earlier one. Build every release
   marked now, in dependency order.
4. **Check prerequisites.** Run each one and record the result. A failed prerequisite
   blocks only the tasks that need it.
5. **Split into tasks.** One reviewable outcome per task, with its files, interfaces
   and checks. Write the shared contract before any task that reads it. Record the
   task graph and merge order in the state file.
6. **Dispatch.** Save each brief, then start every ready task in parallel, up to the
   host's worker limit. Start a dependent task after its prerequisites pass their
   merge checks.
7. **Review each handoff.** Read the worker's diff and test output yourself. A worker
   reporting success means ready for review. Send fixes back to the same worker.
8. **Merge.** Merge accepted work in dependency order and rerun the checks on the
   combined result. A task is `integrated` when those checks pass.
9. **Prove each release.** Walk its acceptance journeys on the combined result with
   `workflow-verify` and `qa`. The next release starts after this checkpoint is green.
10. **Hand off.** Finish with `workflow-handoff` and stop for the user's manual test.

## Workers

- Use the host's delegation tool, with an isolated checkout per worker when the tool
  supports one. Workers sharing a checkout get disjoint files, and you alone run Git.
- Each worker does one task. It loads `tdd` for behavior changes and shows each test
  red, then green. It works from the brief's test seams and asks you, never the user.
- Workers stay inside their brief. They report out-of-scope work as a finding and
  leave nested workers, merges, pushes and deploys to you.
- Use the model and effort the user or project chose for every worker, and record
  what actually ran. Record a setting the host hides as unknown.
- If the host cannot delegate, say so before building alone.

## While the build runs

- **State file.** Write to it before each operation starts and after it ends.
- **Status questions.** Answer from the state file in four lines: done, running,
  next, blocked on the user.
- **Approvals.** Record each approval and pre-approval the user gives with its exact
  scope. Use a recorded pre-approval without asking again, and stay inside its scope.
- **User changes.** Record the request, send it to the owning worker's fix list, and
  append an amendment to any brief already sent.
- **A failed or missing worker.** Read its checkout and output, confirm it has
  stopped, then give the remaining scope to one replacement.
- **A stuck fix.** After two failed fix rounds on one issue, re-diagnose it and
  rewrite the brief, or ask the user.
- **Waiting.** Follow the host's completion events. While workers run, prepare
  reviews and proof.

## Limits

Building authorizes local work only. Paid calls, real sends, pushes, merges to the
default branch and production changes each need the user's word. A proof that needs a
missing provider, browser or device stays listed as pending.

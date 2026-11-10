---
name: workflow-cycle
description: Route a feature, fix or release request to the right stage and installed skill by task size, from a vague idea through plan, build, proof, review, ship and deploy. Use at the start of any development request.
---

# Development lifecycle

1. Read the project instructions and any plan or build-state file for this work.
2. Size the task with the tier table and name the tier in your first reply.
3. Run the first unfinished stage of that tier by invoking its skill.
4. End each stage reply with `Next: <skill>` and one reason. When the work outgrows
   its tier, name the new tier and continue from its first unfinished stage.

Report a skill that is not installed as missing. `workflow-setup` repairs it when the
user asks. Load `unslop` before writing prose.

## Tiers

| Tier | Fits | Stages in order |
|---|---|---|
| Trivial | One file, behavior unchanged | `verify`, `ship` |
| Small | One to three files, behavior changes, no new interface | `diagnosing-bugs` for a bug, `tdd`, `verify`, `review`, `ship` |
| Medium | A feature inside existing boundaries | `office-hours`, `autoplan`, `tdd`, `verify`, `observability-and-instrumentation`, `review`, `qa`, `ship`, `land-and-deploy` |
| Large | A new boundary, interface or service, or an idea that takes more than two sentences to state | `grill-me`, `office-hours`, `autoplan`, `workflow-build`, `workflow-verify`, `qa`, `workflow-handoff`, then in a later session `review`, `cso`, `ship`, `land-and-deploy`, `canary` |

A repository without `CONSTRAINTS.md` runs `constraint-driven-development` once,
before its first build. Later features read the file.

## Plan

- **Research first.** Find facts in the codebase and on the web yourself. Ask the user
  for product decisions only.
- **One decision at a time.** Ask each open decision as its own question, with your
  recommendation and the real cost of each option.
- **Plan reviews.** `autoplan` runs the CEO, design, engineering and developer
  experience reviews, so the plan is reviewed once. Run `plan-ceo-review`,
  `plan-eng-review`, `plan-design-review` or `plan-devex-review` alone when the user
  names it.
- **A later release of an approved plan** starts at plan review. It skips `grill-me`
  and `office-hours`.
- **Screens.** For UI work, show a mockup of every screen the plan touches and open it
  for the user. Building starts after the user approves the mockup.
- **Interfaces.** Use `codebase-design` and `api-and-interface-design` when the plan
  adds a module boundary or public interface.

The plan is ready when it holds numbered acceptance journeys with awkward inputs, the
public test seams, a prerequisites list, the release dependency order and the approved
mockups. Then write the build prompt for a fresh session.

## Build and prove

- **Large builds** run in a fresh session with `workflow-build`. Smaller tiers build
  in the current session with `tdd`.
- **Bugs.** Run `diagnosing-bugs` and get a command that fails on the bug before
  changing code. For a written root cause, write up what that run found.
- **Proof.** `verify` runs the repository checks until green. `workflow-verify` adds
  the acceptance evidence. `qa` walks each journey on the real CLI, API, browser or
  device. Passing unit tests leave the journeys unproven.
- **Stop for the manual test.** Finish the build with `workflow-handoff` and wait.
  The user's change requests after testing go through `tdd` and `verify` on the same
  branch.

## Review, ship and land

Each of these stages starts on the user's word for this release.

- **Review.** Run `review` on the real diff. Fix accepted findings, rerun the affected
  checks and journeys, and send findings outside the release to the project's TODO
  list. One review round and one fix round.
- **Ship.** Run `ship`, then watch every pull request from the moment it opens. Ship
  is done when CI is green on the head commit of every pull request. Fix a failing
  check and report a red check as red.
- **Land.** Run `land-and-deploy` in the project's deploy order, for example the API
  before its clients. Confirm the deployed revision and one live journey, then run
  `canary`. Report pending store releases and missing production proof.
- **Clean up.** After the merge, remove the worktrees and branches this work created.

## Lessons

When the user corrects a workflow miss, fix the rule in the astack source with
`workflow-maintain`. An edit to an installed copy is lost on the next update.
After a release, or when the user asks what to improve, `workflow-maintain` runs a
retro on the recent sessions.

Matt Pocock's `handoff` passes work to another model or tool. `workflow-handoff`
reports a finished build to the user.

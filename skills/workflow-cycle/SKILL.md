---
name: workflow-cycle
description: Route a development request through clarification, planning, constraints, orchestrated TDD, proof, review, shipping, and authorized deployment using installed skills.
---

# Development lifecycle

Read project instructions and the current plan/state first. Identify the stage and
scope requested; continue that stage rather than replaying the whole lifecycle.
Use the installed skills below by reading/invoking their actual entrypoints. A stage
is not complete just because its name appears in a checklist. Record outputs and
any missing capability. If dependencies are absent, use workflow-setup when setup
is authorized; do not pretend an unavailable skill ran.

Load `unslop` before authored prose. Follow its writing rules while preserving code,
quotes, evidence, and exact required tool/report formats.

## Clarify and plan

- **Vague idea:** use `grill-me`/`grilling` to settle product decisions. Inspect the
  codebase and research facts rather than making the user supply discoverable facts.
  Observe the user's question pacing. Skip a fresh interview for an already approved plan.
- **Problem and approach:** use gstack `office-hours`, then save its design/plan output.
- **Plan review:** use `autoplan`, or explicitly selected `plan-ceo-review`,
  `plan-design-review`, `plan-devex-review`, and `plan-eng-review`. Autoplan already
  orchestrates its applicable reviews; do not repeat them automatically afterward.
  Resolve its owner decisions and approval gate before implementation. Include test
  seams, actor journeys, awkward inputs, prerequisites, and release dependencies.
- **Project quality bar:** read existing CONSTRAINTS.md. Use
  `constraint-driven-development` if it is missing or the user wants to change the
  bar. This is project setup, not an interview to repeat on every feature. Retain
  project-specific design/category-baseline requirements for UI work.

## Build and prove

Use `workflow-build` as the orchestrator: graph dependencies, assign small parallel
worker tasks, keep a persistent ledger, review results, integrate, and recover on
restart. Workers use the installed `tdd` skill for behavior changes: agree public
seams, observe one failing test, implement enough to pass, and repeat vertically.
Seams explicitly covered by the user's approved plan are already agreed; do not
re-ask workers' approval questions. Use `codebase-design` when interface design needs
it. A prose-only change does not require invented behavior tests.

Run project check lanes through `workflow-verify`. Walk the plan's actual journeys
with gstack `qa` on the relevant CLI/API/browser/native interfaces. Review changed
screens against the project's design rules. Real provider sends, paid/native checks,
and production operations need the applicable authorization and capability; otherwise
name the missing proof. Unit tests alone do not establish that a feature works.

At build completion, use `workflow-handoff` and stop for the project's manual test
or review gate. The build stage does not automatically authorize shipping. Preserve
workspaces and evidence needed by the next session.

## Review, ship, and land

When requested, run gstack `review` on the actual changes. Fix accepted findings,
repeat affected tests and `qa` journeys, and re-review changed behavior when needed.
The cycle can return to building; keep later evidence tied to the corrected revision.

Use gstack `ship` for the requested release once its required checks/reviews are
satisfied. Ship creates/pushes the reviewable release or PR according to project
policy; do not treat it as evidence of production deployment. Follow host rules for
PR links and asynchronous check waits.

Run `land-and-deploy` only with authorization and after required gates. Respect
cross-repo compatibility and deployment order rather than assuming every repository
can merge at once. Verify the actual deployed revision and live health/journeys,
then the applicable canary. Report pending store releases, missing production proof,
and incomplete CI explicitly. Update the state and final handoff with exact results.

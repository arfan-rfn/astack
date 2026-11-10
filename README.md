# astack

A shared development workflow, from a vague idea to a verified release.

- [workflow-cycle](skills/workflow-cycle/SKILL.md): size the task, then route it through plan, build, proof, review, ship, and deploy.
- [workflow-setup](skills/workflow-setup/SKILL.md): install astack, the pinned upstream skills and gstack for your user on a machine.
- [workflow-build](skills/workflow-build/SKILL.md): orchestrate parallel workers, track progress, integrate results, and resume builds.
- [workflow-verify](skills/workflow-verify/SKILL.md): run project checks and verify acceptance evidence.
- [workflow-handoff](skills/workflow-handoff/SKILL.md): report changes, verification, and unfinished work.
- [workflow-maintain](skills/workflow-maintain/SKILL.md): improve, publish, and update shared skills, and run a retro on recent sessions.

## First-time setup

On a new machine, install astack's skills for your user:

```sh
npx --yes skills add arfan-rfn/astack --skill '*' --agent claude-code codex --global --yes
```

Then start a fresh agent session in any project and ask:

> Use workflow-setup to install the workflow's dependencies on this machine.

Setup needs Git, Node/npm and Bun. It installs the pinned upstream skills and gstack
at user level, so every project on the machine uses the same skills. It shows a diff
and asks before replacing a skill you edited or moving an existing gstack checkout.

The [dependency list](skills/workflow-setup/references/dependencies.json) is the one
place to maintain shared sources and selected revisions:

- Matt Pocock: grill-me and grilling, TDD, codebase design, bug diagnosis, writing for agents, and handoff.
- Addy Osmani: constraint-driven development, interface design, and observability.
- Cursor's pstack plugin: unslop, applied to all prose.
- Gstack: office-hours, autoplan and the four plan reviews, verify, review, QA, security review, ship, land-and-deploy, canary, browse, and write-skill.

Gstack uses its own setup, which workflow-setup runs. Browser readiness is reported
separately from the install.

## Use

Start a fresh agent session in any project and ask:

- "Use workflow-cycle to help me turn this idea into an approved plan."
- "Use workflow-build to implement docs/plan.md with an orchestrator and parallel workers."
- "Use workflow-build to resume docs/plan.md from its saved build state."
- "Use workflow-cycle to review and ship this tested release. Stop before deployment."
- "Use workflow-maintain to improve workflow-build and push the shared-source changes."

workflow-cycle sizes each request as trivial, small, medium or large and runs only
that tier's stages. Constraints are written once per repo. Build sessions prove the
feature and stop for your manual test. Ship is done when CI is green on every pull
request. Review, ship and deploy each start on your word. Existing
project rules, test commands, model choices, and production boundaries stay in force.
Project-specific skills remain owned by their projects.

## Create or improve skills

Edit the files under `skills/` in your astack checkout, never an installed copy. Ask
your agent to use workflow-maintain: it checks the change, commits and pushes when
you ask. To learn what to improve, ask it for a retro on your recent sessions.

## Update a machine

```sh
npx --yes skills add arfan-rfn/astack --skill '*' --agent claude-code codex --global --yes
```

Run it on each machine after astack changes, then start a fresh session. When a pin
in the dependency list changes, ask the agent to run workflow-setup again.

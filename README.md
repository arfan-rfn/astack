# astack

A shared development workflow, from a vague idea to a verified release.

- [workflow-cycle](skills/workflow-cycle/SKILL.md): route clarification, planning, constraints, TDD, proof, review, shipping, and authorized deployment.
- [workflow-setup](skills/workflow-setup/SKILL.md): download upstream skills and integrate the workflow with a project's agent instructions.
- [workflow-build](skills/workflow-build/SKILL.md): orchestrate parallel workers, track progress, integrate results, and resume builds.
- [workflow-verify](skills/workflow-verify/SKILL.md): run project checks and verify acceptance evidence.
- [workflow-handoff](skills/workflow-handoff/SKILL.md): report changes, verification, and unfinished work.
- [workflow-maintain](skills/workflow-maintain/SKILL.md): create, improve, publish, and update shared skills.

## First-time setup

Clone once, or use your existing checkout:

```sh
git clone https://github.com/arfan-rfn/astack.git ~/projects/astack
```

From the target project, ask your agent:

> Read ~/projects/astack/skills/workflow-setup/SKILL.md and use it to install this project's development workflow for Codex and Claude Code. Preserve existing project instructions and report anything unavailable.

Select only the agents you use. Setup needs Git, Node/npm and Bun for gstack. It
installs declared dependencies, copies astack's skills, updates a managed section in
AGENTS.md and the applicable CLAUDE.md, and records effective paths and versions.
It preserves unrelated instructions and stops conflicting replacements with a diff.

The [dependency list](skills/workflow-setup/references/dependencies.json) is the one
place to maintain shared sources and selected revisions:

- Matt Pocock: grill-me/grilling, TDD, and codebase design.
- Addy Osmani: constraint-driven development.
- Cursor's pstack plugin: unslop, applied to authored prose throughout the session.
- Gstack: office-hours, autoplan and individual plan reviews, review, QA, ship, land-and-deploy, and its supporting tools.

Gstack uses its own setup; copying its Markdown is not installation. Cloning astack
alone downloads only astack. Invoking workflow-setup downloads the other pieces.
Browser/native readiness is reported separately from files being installed.

For only astack's Markdown skills, copy the folders manually:

```sh
cd /path/to/your-project
mkdir -p .agents/skills
cp -R ~/projects/astack/skills/. .agents/skills/
```

Use `.claude/skills/` for Claude Code. Keep references with their skill folders.
Manual copying does not install external dependencies.

## Use

Start a fresh agent session in the configured project and ask:

- "Use workflow-cycle to help me turn this idea into an approved plan."
- "Use workflow-build to implement docs/plan.md with an orchestrator and parallel workers."
- "Use workflow-build to resume docs/plan.md from its saved build state."
- "Use workflow-cycle to review and ship this tested release. Stop before deployment."
- "Use workflow-maintain to improve workflow-build and push the shared-source changes."

Constraints are established once per repo and followed on each change. TDD applies
to behavior changes. Build sessions prove the feature and hand off for the project's
manual test; shipping and deployment follow their own authorization gates. Existing
project rules, test commands, model choices, and production boundaries stay in force.
Project-specific skills remain owned by their projects and are inventoried during setup.

## Create or improve skills

Edit the original files under `~/projects/astack/skills/`. For a new skill, create
`skills/your-skill/SKILL.md` with `name` and `description` frontmatter and add it above.
Review changes and any affected setup dependency entries, then publish:

```sh
cd ~/projects/astack
git diff --check
git add skills README.md
git commit -m "Improve development workflow"
git push origin main
```

## Update projects

```sh
git -C ~/projects/astack pull --ff-only
```

Ask the project's agent to use workflow-setup to check and update the installation.
It compares sources, existing content and the setup record before changing selected
entries. Preserve local customizations, finish sessions using old files first, review
the resulting diff, and start a fresh session afterward. Pushing to astack does not
automatically change project copies or authorize global upgrades.

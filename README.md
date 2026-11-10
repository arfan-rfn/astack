# astack

Reusable Markdown skills for building, verifying, and handing off project work.

- [workflow-build](skills/workflow-build/SKILL.md): implement an approved plan and recover interrupted work.
- [workflow-verify](skills/workflow-verify/SKILL.md): run project checks and verify acceptance evidence.
- [workflow-handoff](skills/workflow-handoff/SKILL.md): report changes, verification, and unfinished work.
- [workflow-maintain](skills/workflow-maintain/SKILL.md): create, improve, publish, and update shared skills.

## Install

Keep the shared source at `~/projects/astack`. Clone it once, or use your existing checkout:

```sh
git clone https://github.com/arfan-rfn/astack.git ~/projects/astack
```

From a project directory, copy the skills:

```sh
cd /path/to/your-project
mkdir -p .agents/skills
cp -R ~/projects/astack/skills/. .agents/skills/
```

For Claude Code, use `.claude/skills/` as the destination. You can copy individual
skill folders; keep each folder's referenced files with it. Commit the copied folders
with your project.

## Use

Start a new agent session in your project and ask:

- "Use workflow-build to implement docs/plan.md."
- "Use workflow-verify to check this work."
- "Use workflow-handoff to prepare a handoff."
- "Use workflow-maintain to improve workflow-build and push the shared-source changes."

Project instructions own the architecture, commands, and release rules. Projects
using gstack install it separately.

## Create or improve a skill

Edit the original files under `~/projects/astack/skills/`. For a new skill, create
`skills/your-skill/SKILL.md` with `name` and `description` frontmatter like the existing
skills, and add it to the list above. To update an existing skill, edit its current file.

Review the changes, then publish them:

```sh
cd ~/projects/astack
git diff --check
git add skills README.md
git commit -m "Improve workflow-build instructions"
git push origin main
```

## Update project copies

Pull the latest shared source:

```sh
git -C ~/projects/astack pull --ff-only
```

Review the changes and preserve project-specific edits before replacing copies.
After sessions using those skills finish, repeat the install copy command in each
project. Review `git diff -- .agents/skills` and commit the update there. Start a fresh
agent session to use it. Pushing to astack does not automatically change project copies.

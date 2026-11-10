# astack

Reusable Markdown skills for building, verifying, and handing off project work.

- [workflow-build](skills/workflow-build/SKILL.md): implement an approved plan and recover interrupted work.
- [workflow-verify](skills/workflow-verify/SKILL.md): run project checks and verify acceptance evidence.
- [workflow-handoff](skills/workflow-handoff/SKILL.md): report changes, verification, and unfinished work.

## Install

Clone this repository and copy the skill folders into your project:

```sh
git clone https://github.com/arfan-rfn/astack.git
mkdir -p /path/to/project/.agents/skills
cp -R astack/skills/. /path/to/project/.agents/skills/
```

For Claude Code, use `.claude/skills/` as the destination. You can copy individual
skill folders; keep each folder's referenced files with it.

Ask your agent to use `workflow-build`, `workflow-verify`, or `workflow-handoff`.
Project instructions own the architecture, commands, and release rules. Projects
using gstack install it separately.

To update, review the changes at the desired Git revision, then copy the folders
again after sessions using them finish. Preserve any project-specific edits.

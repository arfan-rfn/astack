---
name: workflow-setup
description: Install or update the astack workflow for this user on this machine by installing astack's skills, the pinned upstream skills and gstack at user level. Use on a new machine, or after astack or its dependency list changes.
---

# Set up the development workflow

Setup installs at user level, so every project on the machine uses the same skills.
[The dependency list](references/dependencies.json) is the only inventory. Install
exactly what it names.

## Steps

1. **Check tools.** Git, Node with npm, and Bun for gstack. Report a missing tool and
   stop the steps that need it.
2. **Inventory.** Run `npx --yes skills@<skills_cli> list -g` and read the revision of
   `~/.claude/skills/gstack`. Mark each dependency missing, current, outdated or
   locally edited.
3. **Show the plan.** Print what you will install, update, keep and skip. For a
   locally edited skill, show the diff and keep it until the user decides. The user's
   request to install covers the rest of the plan.
4. **Install astack's skills** with the first command below.
5. **Install the portable skills** with the second command, one entry at a time.
6. **Set up gstack** with the recipe below.
7. **Verify.** Every skill in the dependency list and every astack skill resolves for
   each selected agent, and each name appears once.
8. **Report** installed, kept and blocked items. Tell the user to start a fresh
   session, since a running session keeps the skills it loaded.

## Commands

Agents are `codex`, `claude-code` or both. Run installers one at a time, because they
share the user-level lock file.

```sh
npx --yes skills@<skills_cli> add arfan-rfn/astack --skill '*' --agent <agents> --global --yes
npx --yes skills@<skills_cli> add <url> --skill <names> --agent <agents> --global --yes
```

- `<url>` is `https://github.com/<repository>/tree/<revision>[/<subdirectory>]`.
- After the installs, apply each `installed_frontmatter` patch the dependency list
  declares. The `unslop` patch turns on model invocation because this workflow
  applies it to all prose. Reapply it after every update.
- `grill-me` routes to `grilling`. Install both.
- The CLI installs Claude Code skills into `CLAUDE_CONFIG_DIR` when that variable is
  set. A user with several Claude config folders runs both commands once per folder.

## gstack

gstack has its own installer. The skills CLI and a Markdown copy both leave it broken.

1. Clone `https://github.com/<gstack.repository>` into `~/.claude/skills/gstack`
   when the folder is absent.
2. An existing checkout at another revision, or with local changes, is the user's.
   Show its revision and status and ask before moving it.
3. Check out the pinned revision and read its `setup` script.
4. Run `./setup --host claude --no-prefix --no-team`, then the same with
   `--host codex`, one at a time. Add `--no-browser` only when the user asks.
5. Run `./setup --status`. Every skill under `gstack.required` is registered under
   its short name, for example `review`. Record a browser that failed to install as a
   missing capability.

Investigate any nonzero exit before continuing.

## Updates

After astack changes, run the first command again on each machine. After a pin
changes in the dependency list, rerun this skill. `/gstack-upgrade` moves gstack past
the pin, so record the new revision in the dependency list once it proves good.

## Project block

A project needs nothing installed. When the user asks to route one project through
the workflow, add the block from [agent-block.md](references/agent-block.md) to its
`AGENTS.md`.

Setup installs skills. Product interviews, builds, paid calls and deploys belong to
later sessions.

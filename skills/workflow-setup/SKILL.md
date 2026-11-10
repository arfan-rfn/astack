---
name: workflow-setup
description: Set up or update a project's astack workflow by downloading declared upstream skills, preparing gstack, and integrating existing agent instructions.
---

# Set up the development workflow

Use [the dependency list](references/dependencies.json) as the single inventory of
shared upstream requirements. The selection is explicit: do not install every
skill found on the machine. This is an agent-run installer using existing Git, npm,
and upstream setup tools; it needs no astack Python package or background service.

## Discover and prepare

Resolve the target project and the astack source checkout. Read existing `AGENTS.md`,
`CLAUDE.md`, constraints, package metadata, and project/user skill discovery roots.
Identify the active/requested agent; current recipes cover Codex and Claude Code.
Check Git, Node/npm, and Bun for gstack. Report missing prerequisites rather than
silently installing system packages or claiming a complete setup.

Inventory skills already routed by project instructions and, when accessible,
relevant recent sessions. Record names, actual source, version, discovery path, and
local edits without collecting credentials. Compare them with the dependency list.
Use verified sources for missing requirements. Report additional project-specific
skills separately. Reuse or install project-required additions when the project's
own repository or lock establishes their source; leave unresolved sources blocked.
Do not publish private skills or silently add them to the shared dependency list.
`grill-me` is Matt's router to `grilling`; install both, not a new handwritten alias.

Present the planned changes, then carry out the requested project-local setup.
An invocation to install authorizes that setup; do not ask again for each ordinary
file. Reuse verified matching installations where possible. Do not replace a global
installation or files used by a running session. Preserve edited copies and show
conflicts before overwriting. Stage downloads separately and serialize installers
within a project, since they share the skills lock and discovery directories.

## Install portable skills and astack

For each package in the dependency list, build its URL as
`https://github.com/<repository>/tree/<revision>[/<subdirectory>]`. From an empty
staging directory, use the declared CLI release:

```sh
npx --yes skills@<skills_cli> add <url> --skill <selected-names> --agent <agents> --yes
```

Use `codex`, `claude-code`, or both as requested. Omit global flags. Keep complete
skill folders, including references, and retain upstream license notices when
redistributing them. The manager owns `skills-lock.json`: never hand-edit it or
replace an existing project lock with the staging lock. For the real project, run
only the reviewed missing/updated selections after conflict checks; inspect that
the manager preserved unrelated lock entries and recorded the exact `ref` values.
Do not rely on a lock alone to accept an edited existing directory.

Copy astack's own skill folders from the selected checkout into `.agents/skills`.
For Claude, use relative aliases from `.claude/skills` to that canonical content,
or verified equal copies if symlinks are unavailable. Do not duplicate a compatible
installation under several names. For a Claude-only project, its discovery path
still needs to resolve every selected skill.

Apply only the dependency list's declared frontmatter adapter changes to installed
copies. Unslop's explicit-only upstream setting is changed to `false` to honor this
workflow's always-on prose preference. Record that patch; do not modify upstream
source or overwrite other local customizations. Keep the upstream license with it.

## Prepare gstack with its own setup

Do not install gstack by copying its Markdown or through the generic skills CLI.
Fetch the exact declared commit into `.agents/astack-tools/gstack`; verify its origin
and revision. Read that revision's setup before running it. Keep its license and
supporting binaries/resources intact.

Scope setup's provider and state roots to this project:
`CODEX_HOME=<project>/.agents`, `CLAUDE_CONFIG_DIR=<project>/.claude`, and
`GSTACK_STATE_ROOT=<project>/.gstack/astack`. These are setup/helper scopes, not
instructions to relocate an agent's credentials or change its launch environment.
Use stock `./setup --host codex --global --prefix --no-team --no-harness-auto`,
or `--host claude`; run each separately for both agents. Here `--global` is scoped
by those provider roots. Never run it with unverified roots pointing to user globals.
Disable both `auto_upgrade` and `update_check` using this revision's gstack-config.
Do not change the runtime provider/model. Record any setup-time rendering profile.

Default upstream setup prepares its browser assets. Use `--no-browser` only when
requested, or report the missing browser capability if preparation fails. Never
claim browser/native proof from helper installation alone. Keep gstack source,
state, and generated `gstack`/`gstack-*` discovery entries local and ignored in Git;
add only these owned patterns to the project's ignore rules, preserving existing ones.

## Integrate and verify

Add or update the small [managed agent block](references/agent-block.md) in AGENTS.md,
preserving all other content. Integrate CLAUDE.md only for Claude: retain its existing
instructions and add a managed pointer to AGENTS.md if needed. Do not append duplicate
routing blocks or weaken project-specific approval, testing, or deployment rules.

Verify selected skill names, complete references, licenses, duplicate discovery,
relative aliases, manager refs, and gstack's source/config/generated helpers. Map
short lifecycle names to actual registered names such as `gstack-qa`; distinguish
astack's `workflow-verify` from unrelated skills named `verify`. Reuse project-specific
skills such as screen-check or agent-capability only when that project requires them.

Write a concise `.agents/astack-setup.md` record: astack revision, selected upstream
commits, CLI/tool versions, effective skill paths, declared patches, content identities,
capability results, and remaining conflicts. Exclude credentials and private session
content; prefer project-relative paths and timezone-aware verification timestamps.
A rerun compares existing content to the recorded/pristine identities and
changes only missing or explicitly updated entries; an edited managed file stops
that replacement with a diff. Leave unrelated files, locks, and settings intact.

Finish with installed/reused/blocked items and tell the user to start a fresh agent
session. Cloning astack alone does not run setup. Do not start a product interview,
TDD cycle, paid model call, deployment, or feature build while installing its skills.

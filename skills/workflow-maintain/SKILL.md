---
name: workflow-maintain
description: Create or improve shared skills, publish requested changes, and update selected project copies.
---

# Maintain shared skills

Locate the shared source repository and confirm its Git remote, README, and working
tree before editing. A skill installed in a project is a copy: do not mistake that
project's repository for the shared source. Preserve unrelated changes.

Read the affected skill and its references. Make the smallest change that addresses
the request. Keep project-specific commands and architecture rules in the project.
Keep credentials, private client material, and machine-specific paths out of shared files.
Preserve existing skill names unless a rename is requested, and check callers before
removing a referenced file. Prefer improving an existing skill over adding an overlap.

For a new skill, create `skills/<name>/SKILL.md` with YAML frontmatter containing
`name` and a description of when to use it. Match the folder name to the declared
name using lowercase letters, digits, and hyphens. Add supporting files only when
they serve the skill; avoid unrequested install machinery and placeholder scaffolding.
For upstream dependencies, update workflow-setup's central dependency list, verify
the pinned source and license, and test its setup recipe. Do not scatter pins across
individual skills or silently upgrade consuming projects.

Check frontmatter, relative links, and consistency with the requested behavior.
Walk through a representative request to catch missing steps or unintended actions.
Confirm referenced files travel with the skill folder. Update README usage examples
when behavior changes, and run `git diff --check`. Report whether validation was
static inspection, a copy check, or an actual agent trial.

If publishing was requested, review the final diff, commit only the intended files,
and push to the agreed remote and branch following repository rules. Never force-push.
If the push is rejected, inspect the remote changes before reconciling them; report
an unresolved failure rather than claiming publication succeeded.

Update project copies only for the projects requested. Review differences and
preserve local customizations before replacing files. Wait for sessions using those
files to finish, then copy the selected folders and references. Check the resulting
diff and use a fresh session to load the update. Updating shared source does not
automatically update project copies. This procedure also applies to this skill itself.

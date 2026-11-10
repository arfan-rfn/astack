---
name: workflow-maintain
description: Create or improve a shared astack skill, run a retro on recent sessions, bring a lesson back to the source, publish it and update the installed copies. Use when the user asks to change, fix or add a workflow skill.
---

# Maintain shared skills

The astack repository is the source. The skills installed on a machine are copies.

1. **Find the source.** Locate the astack checkout and confirm its remote and a clean
   working tree. Keep unrelated changes.
2. **Retro, when the user asks what to improve.** Follow [retro.md](references/retro.md).
3. **Bring lessons back.** When the fix was made in an installed copy or a project's
   own skill, diff it against the source and move the general rule into the source. Project commands,
   architecture rules, credentials and machine paths stay in the project.
4. **Edit.** Load `writing-for-agents` and `write-skill` first. Make the smallest
   change that covers the request. Write numbered steps with a clear done condition,
   state the wanted behavior, and cut any sentence the agent would follow anyway.
   Improve an existing skill before adding one that overlaps it.
5. **New skill.** Create `skills/<name>/SKILL.md` with `name` and a `description`
   that says when to use it. The folder name matches `name`, in lowercase letters,
   digits and hyphens. List it in the README.
6. **Upstream dependency.** Edit only `workflow-setup/references/dependencies.json`.
   Confirm the pinned revision contains the skill and its license, then test the
   setup recipe.
7. **Check.** Frontmatter parses, relative links resolve, referenced files sit inside
   the skill folder, and `git diff --check` is clean. Walk one real request through
   the changed skill. Report whether you inspected it, copied it or ran an agent on it.
8. **Publish when asked.** Review the diff, commit the intended files and push to the
   agreed branch. If the remote rejects the push, read the remote changes and report
   it. Force-push stays off.
9. **Update the machine when asked.** Rerun the astack install command from
   `workflow-setup`, then start a fresh session. A changed pin needs a full
   `workflow-setup` run.

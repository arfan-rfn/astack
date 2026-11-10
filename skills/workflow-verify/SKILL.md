---
name: workflow-verify
description: Collect acceptance evidence for the current revision before reporting a build or fix complete. Use after the repository checks pass and before a handoff.
---

# Verify the current revision

1. **Checks.** Run the project's checks at the required scope, with gstack `verify`
   where installed. Fix the code until they pass. The checks, coverage floors and
   database serialization stay as the project defines them.
2. **Journeys.** Walk every accepted journey through its real interface, including
   awkward inputs and failures. Use the project's QA procedure and gstack `qa` for
   the matching CLI, API, browser or device. A CLI is tested from the shell.
3. **Record.** For each check and journey, write the command, working directory, exit
   status, revision and evidence path. Keep the original failure beside its fix.
4. **Label the evidence** as static inspection, fixture replay, live run or
   production proof.
5. **Pending proof.** List each check you could not run with what it needs. An
   unavailable check counts as pending.

Evidence is valid for the revision it ran on. Rerun what a later edit touches.

# Retro on recent sessions

A retro finds where the workflow skills failed the user and proposes the smallest
fix for each. The method follows Matt Pocock's `retro` skill, with two checks added
for skill coverage. gstack's `retro` is a different tool that reports git metrics.

1. **Scope.** Use the sessions the user names. Otherwise use the last seven days of
   this project's session logs for the agent you are running in.
2. **Extract with a script.** Pull the user's typed messages and the skill
   invocations out of the logs. Whole transcripts stay out of your context.
3. **Find candidates** in these categories:
   - **Missing skill.** A skill the sessions invoked that the dependency list lacks.
   - **Repeated correction.** Something the user corrected or asked for more than
     once.
   - **Skipped stage.** A stage the tier required that did not run, or ran late.
   - **Missing check.** A mistake an automated check would have caught. Propose the
     check before proposing a written rule.
   - **No-op.** A skill or instruction line that changed nothing in any session.
   - **Missing information.** A fact the agent needed and could not reach, such as
     server logs.
4. **Present** the candidates ranked by how often each occurred, with the session
   and message as evidence and the proposed edit. One-off events are left out.
5. **Edit** only the candidates the user accepts, through the remaining steps of
   `workflow-maintain`.

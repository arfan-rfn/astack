# Project agent integration

Maintain exactly one block with these markers in the project's AGENTS.md. Keep the
project's existing instructions outside it unchanged. If an existing managed block
was customized, show the diff and reconcile it before replacement.

```markdown
<!-- astack:workflow:start -->
## Development workflow

Start every feature, fix or release request with the workflow-cycle skill. It sizes
the task and names the next skill to run.
Load unslop before writing prose, comments, commits and PR text.
This project's constraints, check commands and approval gates take priority.
<!-- astack:workflow:end -->
```

For Claude, when CLAUDE.md does not already load AGENTS.md, preserve its existing
content and add one managed pointer:

```markdown
<!-- astack:workflow:start -->
Read AGENTS.md for the shared development workflow and project rules.
<!-- astack:workflow:end -->
```

Publishing, spending, production changes and the manual acceptance gate still need
the user's word.

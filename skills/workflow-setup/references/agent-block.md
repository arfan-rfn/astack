# Project agent integration

Maintain exactly one block with these markers in the target AGENTS.md. Keep the
project's existing instructions outside it unchanged. If an existing managed block
was customized, show the diff and reconcile it before replacement.

```markdown
<!-- astack:workflow:start -->
## Development workflow

Use the installed workflow-cycle skill to route development work from idea through
planning, orchestrated building, proof, review, shipping, and authorized deployment.
Follow this project's constraints, check commands, product rules, and approval gates.
Load unslop before the first authored response and use it for prose, documentation,
comments, commits, and PR text. Preserve code, quoted evidence, and required tool formats.
For gstack helper commands, scope GSTACK_STATE_ROOT to this project's .gstack/astack.
Set GSTACK_PLAN_DIR to the plan root recorded by setup, preserving existing project plans.
Use actual registered skill names and paths from .agents/astack-setup.md. If a required
skill is missing, report it and use workflow-setup to repair the requested installation.
<!-- astack:workflow:end -->
```

For Claude, when CLAUDE.md does not already load AGENTS.md, preserve its existing
content and add one managed pointer:

```markdown
<!-- astack:workflow:start -->
Read AGENTS.md for the shared development workflow and project rules.
<!-- astack:workflow:end -->
```

Installation supplies instructions, not permission to publish, spend money, alter
production, or bypass a project's manual acceptance gate.

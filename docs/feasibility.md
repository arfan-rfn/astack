# Upstream feasibility

Verified locally on macOS, 2026-11-10 UTC. Private raw logs and installation records
are retained under `.local/` and the private host state root.

## Gstack

Source: `https://github.com/garrytan/gstack.git`, commit
`b6155921a564ba9ec2470fd2cb3894c05e2c2d13` (version 1.98.0.0).
The commit was fetched from upstream, not inferred from an existing working copy.
Preparation ran stock setup with explicit Codex host, separate provider/state roots,
`--global --no-team --prefix --no-browser --no-harness-auto`. Here `--global` grants
replacement only inside the isolated provider root; no live user installation changed.

Setup completed, generated discoverable prefixed Codex directories, built the browser
helper, and left tracked upstream source clean. Both `auto_upgrade` and `update_check`
are explicitly false. A real `gstack-skill-start --skill qa --model codex` completed
without advancing the source commit or changing the rendered-content identity.
The identity includes generated helper bytes and executable modes, separately from
the pristine Git revision. Re-running prepare on verified content performs verification.

A second generation at the prior commit
`199931029e9fe9808554a4863c960d4b9b663a60` also prepared independently. The source diff
was inspected: the selected revision fixes pre-push stray-file detection and adds
tests/docs. Verifying each generation after preparing the other proves their source,
rendered instructions and state roots coexist. Switching a running agent's environment
is deliberately unsupported; launch a fresh session against the selected record.

Limits: upstream labels Codex experimental. Bun 1.3.11 completed the setup but upstream
warns that its tested version is 1.4.2. Chromium was not installed and no browser journey
was claimed. Actual Codex/Claude model-driven discovery trials, the Claude upstream
adapter, and Linux startup remain pending. The current agent read the generated files;
this is static integration evidence, not a fresh agent discovery trial.

## Skills CLI

Selected `skills@1.7.6`, with npm SHA-512 integrity in `tools.lock.json`. The wrapper
asks npm to generate a package lock, checks the selected package's version/integrity
against that approved record, and uses `npm ci --ignore-scripts` before execution.
The CLI retains ownership of `skills-lock.json`.

The selected CLI's `experimental_install` skips any existing skill directory unless
`--force` is supplied. The wrapper therefore only restores to a nonexistent isolated
candidate, always with `--force --frozen-lockfile`, and checks that every locked skill
was actually restored before success. A frozen lock that cannot reproduce its content
fails; the wrapper never changes the lock to accept current upstream.

A real restore of the existing API pilot lock failed with:

```text
Cannot install with --frozen-lockfile because skills-lock.json is not up to date:
neon has changed since skills-lock.json was written
```

Its original lock and installed content are preserved. Historical restoration of that
third-party dependency remains pending. This is a limitation of the observed lock,
not evidence that every skills CLI lock is unreproducible. Owned astack snapshots use
exact Git blobs and do not rely on this failed restoration path.

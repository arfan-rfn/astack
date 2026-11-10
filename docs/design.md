# Astack implementation decisions

The shared source is named **astack**, per the implementation-session rename.
The original PLAN.md is retained as the rollout contract, including its former name.

## Runtime and dependency ownership

Use Python 3.11+ and its standard library on POSIX hosts. This avoids a runtime
package download for contributor checks. JSON descriptors are deliberately explicit.
Owned skills are selected from an immutable Git commit using Git, copied into the
project, and recorded in `.workflow-managed.json`. This file owns only astack files;
it never edits `skills-lock.json`. Third-party portable skills remain owned by
skills CLI 1.7.6. Gstack uses its own setup in a separate provider/state root.

Rejected: a package registry, a general-purpose replacement skill manager, moving
release labels at startup, copying a global home directory, or patching upstream.

## Activation and recovery

The activation unit is one project. A host-local flock serializes mutations and
session lease creation. Updates prepare a complete candidate without changing the
project. Activation checks managed-file identities and rejects collisions, edits,
unmerged files, symlink parents, and open session leases. Each transaction first
saves the exact owned bytes, modes, and link targets and a durable write journal.
Exceptions restore those bytes. After process termination, `doctor` rejects a
pending journal and `bootstrap` restores it before any subsequent activation.
No global settings, hooks, or registrations are adopted, so rollback does not need
to rewrite shared settings files. New unrelated files survive rollback.

POSIX does not provide a portable atomic multi-file project checkout operation.
An interrupted activation therefore requires journal recovery before a new session
can start. Previous bytes are retained, but direct agent launches bypass this gate.
Use `workflow run -- <agent command>` for managed sessions. Existing independently
launched sessions cannot be reliably discovered; activation also requires a local
host descriptor declaring that the target has been drained. Never auto-expire a
lease just because its PID disappeared. Inspect it and close it explicitly.

Rejected: replacing live global skills, guessing session liveness from process
names, deleting locks on a timer, and restoring whole settings files.

## Scope of certification

Deterministic tests certify installation mechanics. They do not certify an agent's
future behavior. Native capabilities and actual agent discovery require recorded
trials on each OS/adapter. Missing remote links and maintainer decisions are rollout
exceptions, not simulated passes. Publication remains a separate visibility decision.

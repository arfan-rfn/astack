# Verification and rollout status

The shared source is implemented locally as **astack**. This is a staged rollout,
not a claim that all projects or hosts have migrated. Machine paths, proposal heads,
archives and per-project/host/adapter rows are kept in the private `.local/rollout.json`.
The original planning document is local-only because it contains project inventory.

## Evidence

- `make check`: 28 deterministic regression tests, compile check and diff whitespace
  check on local macOS/Python. Tests cover exact source blobs, idempotence, edited and
  unmerged files, missing references, duplicate discovery, copy/symlink adapters,
  candidate identity, malformed descriptors, lock contention, session leases, write
  failure, interrupted journal recovery, concurrent edits, scoped capabilities,
  configuration staging and rollback preserving unrelated files/settings.
- A fresh clone of this source runs the contributor checks without private project
  files or an AI subscription. The CI matrix is configured but has not run remotely.
- Both isolated project proposals bootstrap twice, pass doctor, and use shared
  revision `c997a6b84d205167f074f55136b2489910eeb221`. Their vendored CLIs work outside
  the shared source; upstream verification also runs through the vendored wrapper.
- Wadi: its real `make lint typecheck` passed after aligning portable source formatting
  with its existing rules; its bounded contracts suite passed **281 tests**. The
  architecture decision precedes adoption. A new tracked AGENTS.md routes to tracked
  CLAUDE.md; the original checkout's untracked instructions were not staged.
- Connecto API: `pnpm check:fast` passed; focused capability-ledger and workflow-path
  tests passed **36 tests**. Current typed contracts and tests support the richer
  capability guidance selected for the canonical `.agents` copy. Three other duplicate
  directories were byte-identical and became relative Claude aliases. Previous copies
  are archived privately; stamp readers now use the canonical path. No DB suite, paid
  provider call, real send or production task ran.
- Candidate staging, activation, rollback and reactivation ran through the actual CLI
  in both proposals. Staging left stable content unchanged; rollback restored the
  previous manifest and descriptor. Subsequent adoption included the approved tool
  lock and standalone upstream wrapper through a staged descriptor proposal.
- Upstream setup/startup and the existing third-party lock failure are documented in
  [feasibility](feasibility.md). The conflicted global checkout was preserved.
- A same-provider native adversarial reviewer found issues that were fixed with
  regression coverage. This is not independent-model review. Gstack QA's functional
  methods and evidence recorder were used for CLI checks; no browser was required.
  A formal full gstack plan-review/ship cycle was not claimed.

## Acceptance matrix

| Case | Verified | Remaining boundary |
|---|---|---|
| V1 exact restoration | Owned snapshots and clean pinned gstack | Existing Neon historical lock fails frozen restoration |
| V2 idempotence | Tests and both project bootstraps | Remote hosts pending |
| V3 preservation | Local edit, real unmerged-index rejection, private duplicate archive | Live global replacements were not attempted |
| V4 discovery drift | Duplicate names, wrong declared names, links and required references | Actual agent discovery trials pending |
| V5 adapter use | Static paths, relative aliases and standalone CLIs | Model-driven trial for each adapter pending |
| V6 capabilities | Required/optional probes and recorded outcomes | Linux and native testing pending |
| V7 upstream pin | Real setup/startup with unchanged source/render identity | Other adapters/OS combinations pending |
| V8 recovery | Injected write failure, interrupted journal and concurrent-edit refusal | A killed activation requires recovery before new launch |
| V9 serialization | Separate-process flock test | No cross-machine shared filesystem is supported |
| V10 rollback | Owned byte/link/mode restoration; unrelated settings retained | No global setting keys/hooks were adopted |
| V11 session safety | Durable leases and explicit drain gate | Direct agent launches require operator drain; they bypass leases |
| V12 portability | Fresh source clone and standalone project snapshots | Full clean contributor application suites not run |
| V13 enrollment | Generic identifier/path/capability maps, two project profiles | No linked remote environment available |
| V14 project quality | Existing check definitions retained; fast/focused checks pass | Full app, Scala, browser/native and authenticated suites not claimed |
| V15 independent updates | Owned bundle rollback drill and separate upstream generations | Remote rollback and broader promotion pending |

## Remaining adoption gates

Wadi and API changes are **proposal commits in isolated clones**, not changes to
working feature checkouts. Actual agent discovery trials and resolving the historical
third-party lock precede broader adoption. No linked remote environment was available;
remote setup/rollback remains pending rather than treated as migrated.

Workspace versioning, web/mobile rollout, repository-boundary discovery for additional
workspaces, and external/client project integrations retain their plan boundaries.
External-governance projects remain local-only/pending; private/client material is
excluded from shared source. No production or deployment configuration changed.
The publication target is the owner's existing public repository,
`https://github.com/arfan-rfn/astack`. Private runtime evidence and pilot checkouts
remain excluded. No pilot adoption PR, merge or deployment has been performed.

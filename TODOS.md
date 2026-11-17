# TODOS

## Workflow cycle

### Decide whether council may run past one review round

**What:** State in workflow-cycle whether `council` is exempt from "One review round and one fix round".

**Why:** `council` repeats until all three models are satisfied. workflow-cycle allows one review round. An agent that gets both instructions has to guess.

**Context:** `council` was added from tstack on 2026-11-17 and sits outside the tiers. workflow-cycle says when to run it and nothing about rounds. The recommended default is to keep the one-round rule and ask for a loop in words when one is wanted.

**Effort:** S
**Priority:** P2
**Depends on:** None

### Decide who wins on force-push: babysit-pr or gstack ship

**What:** Say whether `babysit-pr` may rebase a pull request branch and push with `--force-with-lease` during Ship.

**Why:** `babysit-pr` rebases when the base branch moves. gstack `ship` says never force-push. The Ship stage runs both and names no order of precedence.

**Context:** Raised by the adversarial review of the tstack change. The case appears only when the base moves while a pull request is open. `land-and-deploy` may already cover a branch that is behind, which would make the rebase unnecessary. Check that first.

**Effort:** S
**Priority:** P2
**Depends on:** None

### Limit what babysit-pr reads and posts on a public repository

**What:** Decide whether `babysit-pr` may act on comments from any account, and whether it may reply and resolve threads without the user's word.

**Why:** Its watcher wakes the agent with comment text from every account except the author and the `gh` user. On a public repository a stranger can reach an agent that holds push rights. It also replies under the user's account, while the project block says publishing needs the user's word.

**Context:** `babysit-pr` tells the agent to verify each finding against the source before changing code, which limits the risk but does not remove it. gstack's own watcher strips control characters from event lines and the tstack script does not.

**Effort:** M
**Priority:** P2
**Depends on:** None

### Match the Ship stop condition to how the watchers exit

**What:** Rewrite the Ship line so each case names an exit the watcher has.

**Why:** Three cases have no instruction today. `pr-wait --until green` exits when required checks pass, so a slower optional check is not waited for. A pull request that triggers no checks in a repository with CI never makes the watcher exit. A review bot that posts after the watch stops is never read, and a repository with review bots but no CI gets no watch at all.

**Context:** Found by the fix-check on 2026-11-17, after one fix round on the Ship line. The stop rules live in the upstream skill, so the fix may be a pinned newer tstack revision and not more words in workflow-cycle.

**Effort:** M
**Priority:** P3
**Depends on:** None

## Workflow setup

### Make the tool check match what the tstack skills need

**What:** Decide what setup does when Python 3.9 or `gh` is missing, and say that `council` needs a host that can reach three providers.

**Why:** Step 1 checks Python but no setup step needs it, so nothing stops and step 7 passes with a watcher that cannot run. `gh` is not checked. `council` reports and stops on a host that runs one provider's models.

**Context:** `babysit-pr` uses its Python watcher only outside T3 Code. In T3 Code it uses `watch_pull_request`, and `council` uses `delegate_task`.

**Effort:** S
**Priority:** P3
**Depends on:** None

## Completed

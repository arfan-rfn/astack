---
name: workflow-handoff
description: Report a finished build or fix to the user with revisions, evidence, manual test steps and open items. Use at the end of a build, before review and ship.
---

# Evidence handoff

Read the project instructions and the saved state, then write the handoff in this
order.

1. **Decisions made for the user.** Every choice the plan left open, with the reason.
2. **Manual test.** Numbered steps with accounts, URLs, inputs and the expected
   result. Leave the dev servers running and list their URLs.
3. **Changed.** Branch and head revision per repository and per release.
4. **Evidence.** Checks and journeys that ran, with results and evidence paths. Name
   any reused result and the revision it came from.
5. **Pending.** Unproven journeys, failing or unfinished CI, and proof that needs a
   provider, device or production, each with its next action.
6. **Next.** The stage that follows, which starts on the user's word.

Honor the project's own summary format when it defines one.

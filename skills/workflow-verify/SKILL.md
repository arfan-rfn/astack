---
name: workflow-verify
description: Check workflow identity, project quality lanes, missing capabilities, and acceptance evidence before reporting completion.
---

# Verify the consumed revision

Read `workflow.json` and run `workflow doctor --project <id> --json` using the local
host mapping. Stop dependent work for required drift, missing references, duplicate
discovery or missing required capability. Optional capabilities remain explicit.

Run the project's declared checks at the required scope. A null lane is unavailable,
never passed. Do not edit checks, lower coverage, suppress assertions, or skip DB
serialization to make migration succeed. Keep schema generation and native-device
proof where project rules require them.

Exercise each accepted journey through its actual interface, including awkward
inputs and failures. Keep evidence for the actual revision after the latest edit.
Distinguish static inspection, fixture replay, live execution, and production proof.
Report unavailable provider/native/remote checks as pending with their prerequisites.

Use the project's gstack QA integration for the relevant CLI, API, browser or native
surface. Never launch a browser solely to test a CLI. See the build skill's state
reference for the evidence fields; preserve the original failed result and its fix.

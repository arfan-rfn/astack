---
name: workflow-verify
description: Check project quality gates, required capabilities, and acceptance evidence before reporting completion.
---

# Verify the consumed revision

Read the project's instructions, approved plan, saved task state, and current Git
diff. Check required references and capabilities. Stop affected work when a required
tool or capability is missing; record the prerequisite and continue independent work.

Run the project's checks at the required scope. An unavailable check is never passed.
Do not edit checks, lower coverage, suppress assertions, or skip DB serialization
to make a change pass. Keep schema generation and native-device
proof where project rules require them.

Exercise each accepted journey through its actual interface, including awkward
inputs and failures. Keep evidence for the actual revision after the latest edit.
Distinguish static inspection, fixture replay, live execution, and production proof.
Report unavailable provider/native/remote checks as pending with their prerequisites.

Follow the project's QA workflow for the relevant CLI, API, browser or native surface,
including gstack where the project uses it. Never launch a browser solely to test a
CLI. Record each command, working directory, exit status, revision and evidence path;
preserve the original failed result and its fix.

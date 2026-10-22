# Q-Batch of Evidence

**Q = QA.** A lightweight method for testing systems in independent batches and comparing the evidence afterward.

Q-Batch grew out of a practical problem: a supposedly blind run can be contaminated by an earlier run in the same conversational or working environment. It also avoids the runtime and coordination costs of keeping comparison runs together.

The core method is simple:

1. **Specify** what each batch is meant to test, what resources it may use, and the response/log/result set it must produce.
2. **Run Batch A** in its specified environment. Collect and preserve its outputs.
3. **Run Batch B** in its specified environment. Collect and preserve its outputs.
4. **Compare offline** against the expectations and, where relevant, against the other batch.

The batches do **not** have to run at the same time, on the same day, one after another, in the same account, or with the same agent. They may deliberately use different resource libraries, includes, instructions, or loading configurations. Those conditions must be declared so the comparison can be interpreted.

## Why use it?

- **Separate execution from evaluation.** The test runtime produces evidence; comparison happens later.
- **Reduce cross-run contamination.** Each batch can start from its own required environment rather than inheriting context from another batch.
- **Make evidence portable.** Another person or agent can inspect the collected artefacts without repeating the run.
- **Support asynchronous work.** Batch A can be archived now and Batch B run later.
- **Compare resource conditions.** Different libraries, includes, versions, or loading strategies can be tested under explicit conditions.

Q-Batch does not guarantee that an environment is clean merely because a new chat or process was started. The relevant reset and persistent-state assumptions should be recorded. If two batches intentionally differ, the result describes that difference; it does not by itself prove which difference caused an observed outcome.

## Start here

- [Specification](SPECIFICATION.md) — the method and minimum records.
- [License](LICENSE) — Creative Commons Attribution-NonCommercial 4.0 International.

## Status

An emerging, practical method. The specification is deliberately small; examples and refinements should follow from real use rather than being invented in advance.

## Name

The `q-` prefix marks this as QA-related work.

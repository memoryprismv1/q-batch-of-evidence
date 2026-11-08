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
- [Peer Review skill](https://github.com/memoryprismv1/cognitive-interface-ai-skills/tree/main/peer-review) — a reusable reviewer behaviour for examining preserved outputs against the predeclared criteria. It does not replace the specification, batch records, or comparison record.
- [License](LICENSE) — Creative Commons Attribution-NonCommercial 4.0 International.

## Status

An emerging, practical method. The specification is deliberately small; examples and refinements should follow from real use rather than being invented in advance.

## Supporting implementation

This repository is also the canonical home for Q-Batch's reference implementation and experimental tools:

- `testing_logger/` — shared append-only Q-Batch event and artifact logger.
- `experiments/ct_ab/` — paired-run harness, event schema, validation, preflight and deterministic method demonstration.
- `experiments/checklist_elaboration/` — four-condition MP × CT planning experiment, frozen task fixture, runner and scoring materials.
- `experiments/qbatch_historical_analysis/` — read-only historical evidence and cohort analysis.
- `experiments/actor_attribution_transfer/` — a six-run batch where T1/T2 conclusions are preserved as portable context and used to test transfer into T3/T4, with immutable run receipts.
- [Pilot plan](PILOT_PLAN.md) — current status and limitations of the AEL-related pilot.

The [Q-Batch regression workflow](.github/workflows/tests.yml) runs deterministic and synthetic test suites. Real-model execution is controlled only by the manual, private [Differential workflow](https://github.com/memoryprismv1/the-differential-library/blob/main/.github/workflows/qbatch-checklist-elaboration.yml); this public repository contains no workflow that uploads raw real-model traces.

## Relationship to AEL

[AEL Runtime Accountability](https://github.com/memoryprismv1/ael-runtime-accountability) is the system under examination. Its append-only ledger records AEL runtime behaviour and decision authority. Q-Batch records test execution, conditions, observed evidence and historical comparisons. A test can produce both receipt streams; they are separate records with separate purposes and schemas.

## Evidence privacy

This repository is public. Do not use its workflows with private prompts, personal or customer data, credentials, confidential source code, or other sensitive inputs. Raw request/response evidence may reveal experimental conditions. The private checklist-elaboration controller workflow, evaluator-only reference and restricted raw evidence remain in The Differential.

## Name

The `q-` prefix marks this as QA-related work.

---
name: ael-qbatch-operator
description: Use for work involving AEL Runtime Accountability and Q-Batch, including implementation, experiments, logging, evidence review and historical comparison.
---

# AEL + Q-Batch Operator

## The two-project boundary

AEL and Q-Batch are separate projects with related but distinct responsibilities.

| Home | Canonical responsibility |
|---|---|
| [AEL Runtime Accountability](https://github.com/memoryprismv1/ael-runtime-accountability) | AEL implementation, canonical append-only AEL ledger, runtime events, decision authority and human handoffs, checkpoint exports, runtime tests and AEL-specific verification. |
| [Q-Batch of Evidence](https://github.com/memoryprismv1/q-batch-of-evidence) | Q-Batch method, experiment specifications, event logger, runners and harnesses, condition manifests, scoring, validation, historical analysis, Q-Batch tests and reports. |
| [The Differential](https://github.com/memoryprismv1/the-differential-library) | Institutional navigation and cross-project history, plus private controller material, evaluator-only references and raw/blinded evidence that must not be in public repositories. It is not a second source-code or experiment archive. |

AEL is the system being examined. Q-Batch is the testing and evidence machinery used to examine it. The original AEL framework and source essays remain the user's work; the runtime repository is an implementation/conformance prototype, not the complete framework.

## Two receipt streams

A single test may produce two distinct streams:

- **AEL ledger receipts** describe AEL's own runtime conduct: recorded events, provenance, decision authority, state transitions and human decision handoffs.
- **Q-Batch receipts** describe the experiment: test and batch identity, runner and model details, conditions, observed requests/responses and tool activity, artifacts, integrity checks, validation, failures and comparisons.

A shared run/correlation identifier may link the two. Do not merge their schemas or treat one as a substitute for the other.

Do not treat `provenance=user` or `authority=user_direct` as proof of a human identity. Distinguish the account/scope, the acting principal, the process executing an action, and the human whose authority is being exercised. Missing identity or producer context is a material limitation in an accountability receipt.

## Work procedure

1. Identify whether the task concerns AEL runtime behaviour, Q-Batch evidence machinery, or an experiment that exercises both.
2. Inspect current repository state, source files, manifests, protocols, workflow configuration and latest CI. A dated status note is not proof of current state.
3. Put AEL runtime changes and AEL ledger verification in AEL. Put test runners, Q-Batch log schemas, logger code, historical analysis, scoring and Q-Batch tests in Q-Batch.
4. Keep private controller keys, hidden evaluator references, raw prompts/responses and restricted evidence in the private Differential archive. Never copy these into public repositories or evaluated-agent workspaces.
5. Preserve source run evidence unchanged. Store derived interpretation in separately identified reports that link to original evidence.
6. Record exact commits, run IDs, protocol versions, checksums, validation results and limitations.

## Checklist-elaboration experiment

The design is a 2×2 comparison: MP off/CT off, MP on/CT off, MP off/CT on, and both on. Keep the factors separate and follow the frozen condition manifest.

- The runner, protocol, task fixture and scoring material live in Q-Batch under `experiments/checklist_elaboration/`.
- The private manual execution workflow and evaluator-only reference live in Differential.
- The condition key must never be mounted in the evaluated agent's workspace or disclosed before blind scoring is frozen.
- The task is planning-only. The simulated `request_input` tool records a hypothetical question and returns no answer; it contacts nobody.
- One run per condition is a feasibility block, not an efficacy study.

## Evidence discipline

Keep completed, failed, incomplete, timed-out, resource-capped/censored, excluded and not-run attempts distinct. Never overwrite a failed attempt with a retry or combine attempts without explicit lineage.

A missing event is not proof an action did not happen unless the capture contract establishes that it was observable and required. Missing identity, producer provenance, environment state or capture coverage must be reported, not guessed.

The historical reader is read-only and does not authorise reruns. A rerun requires a separately justified change, passing regression coverage and explicit execution authorisation.

## Security and privacy

Both AEL and Q-Batch repositories are public. Do not put private prompts, personal/customer data, credentials or confidential source code in public workflows. Public Actions artifacts are accessible to repository readers.

Differential has repository-wide access, not per-folder access. Anyone given read access may be able to see raw evidence and controller keys. Do not give blinded assessors access to Differential; distribute only the intended blinded score packets through a separate restricted channel.

## Interpretation

Do not claim that fake-model tests establish real-model behaviour, that one feasibility block establishes efficacy, or that append-only storage alone establishes accountability. State what each receipt actually proves and what it leaves unknown. Preserve uncertainty instead of filling gaps with plausible narrative.

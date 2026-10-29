# Basic Evidence Log Format

**Status:** Working draft 0.2  
**Purpose:** Domain-neutral evidence record for one independently executed batch. Specialized formats extend this record; they do not redefine it.

## Identity and continuity

Each record represents one attempt. A retry gets a new `batch_id`; failed history is never overwritten.

- `test_id`: stable identity of the logical test/investigation across attempts.
- `batch_id`: unique identity of this execution attempt.
- `run_id`: optional ID assigned by the runner; retain separately from Q-Batch IDs.
- `companion_test_uuid`: optional UUID grouping test records intended to be companions in a comparison or historical series.
- `condition`: role in a comparison (A/B/control/treatment); not an identity.
- `parent_batch_id`: prior attempt this one retries or recovers.
- `comparison_ref`: reference to a separately stored comparison record.

Use distinct IDs for distinct concepts. The companion UUID groups records; it does not prove they are comparable. A comparison must name its actual input batch IDs and criteria.

## Test definition and context

- `summary`, `description`: concise label and scope.
- `purpose`: question or behaviour examined.
- `rationale`: why this test exists; motivating observation or decision.
- `hypothesis`: optional predeclared expectation.
- `origin_refs`: source discussion, issue, paper, requirement, or prior observation.
- `git_refs`: repository, branch, commit, tag, or diff; Git metadata is not a substitute for historical context.
- `method_version`, `specification_ref`: method and frozen test-plan versions/hashes.
- `context`: structured object carrying the background needed to interpret the test without the original chat or author. Include relevant background, assumptions, scope, constraints, dependencies, and known unknowns. Carry the object with each attempt or reference an immutable, versioned context object.

If test purpose or context changes, preserve the old version and record which version each attempt used. Do not let a mutable branch or current README silently redefine historical tests.

## Core execution fields

| Field | Meaning |
|---|---|
| `schema_version` | This format's version |
| `started_at`, `ended_at` | Timezone-aware timestamps, null if unknown |
| `executor` | Executing system/agent/person and version |
| `environment` | Environment, reset/isolation method and limitations |
| `inputs`, `resources` | Inputs and relevant files/instructions/dependencies, with versions/hashes where practical |
| `procedure` | Exact steps, commands, prompts, or procedure reference |
| `status` | `completed`, `failed`, `incomplete`, or `invalid` |
| `events` | Ordered observations, errors, warnings, timeouts and collection gaps |
| `outputs` | Raw output/artifact references, media types and hashes where available |
| `deviations` | Departures from the frozen plan |
| `limitations` | Missing evidence and interpretive limits |
| `provenance` | Collector, collection time and integrity metadata |
| `interpretation` | Null until separately evaluated; keep observations distinct from conclusions |

## Event fields

Where applicable: `event_id`, monotonic `sequence`, timezone-aware `timestamp`, `type`, `actor`, `action`, `observation`, `status`, `evidence_refs`, and `notes`. Keep raw evidence intact. Specialized domains may add event types.

## Minimal JSON template

```json
{
  "schema_version": "basic-evidence-log/0.2",
  "test_id": "stable-logical-test-id",
  "summary": "Short label",
  "description": "Scope and behaviour investigated",
  "purpose": "Question being answered",
  "rationale": "Why this test was initiated",
  "hypothesis": null,
  "origin_refs": [],
  "git_refs": [],
  "method_version": null,
  "specification_ref": null,
  "context": {
    "background": [],
    "assumptions": [],
    "scope": [],
    "constraints": [],
    "dependencies": [],
    "known_unknowns": []
  },
  "batch_id": "unique-attempt-id",
  "run_id": null,
  "companion_test_uuid": null,
  "condition": null,
  "parent_batch_id": null,
  "comparison_ref": null,
  "started_at": null,
  "ended_at": null,
  "executor": {"name": null, "version": null},
  "environment": {"os": null, "reset": null, "limitations": []},
  "inputs": [],
  "resources": [],
  "procedure": [],
  "status": "incomplete",
  "events": [],
  "outputs": [],
  "deviations": [],
  "limitations": ["Template only; no execution has been recorded"],
  "provenance": {"collector": null, "collected_at": null, "integrity": []},
  "interpretation": null
}
```

Null means unknown/not captured, not zero. Never invent values to make a record look complete.

## Historical and comparison rules

1. Freeze the record and raw artifacts for each attempt; hash artifacts when feasible.
2. A correction is a new version/addendum referencing the original, not a silent rewrite.
3. Preserve failures, incomplete attempts, and retries as separate records. Link them with `parent_batch_id`.
4. Keep raw events and outputs in evidence records/referenced artifacts. Aggregates, scores, comparisons and conclusions belong in separate analysis/comparison records.
5. A later conclusion must cite the input batch IDs, test/context versions, criteria, evaluator, and limitations.
6. Avoid secrets and unnecessary personal data in public logs.

## Specialized formats

A derived format must declare the basic schema version it extends, retain applicable base fields with unchanged meanings, add domain fields in a named section, version its schema, define validation/acceptance rules, and distinguish raw evidence from generated summaries. See `formats/SOFTWARE_TEST_LOG.md` and `formats/AEL_RUNTIME_EVIDENCE.md`.

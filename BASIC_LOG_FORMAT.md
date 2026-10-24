# Basic Evidence Log Format

**Status:** Working draft 0.1  
**Purpose:** A small, domain-neutral record for an independently executed batch. Specialized test formats extend this record; they do not replace or redefine it.

## Design rules

- One immutable batch record per execution attempt.
- Preserve observed facts separately from interpretation.
- Record failures, timeouts, missing outputs, and collection failures as first-class results.
- Never silently repair a completed record. Corrections create a new version or an addendum referencing the original.
- Use stable identifiers and explicit links between batch, events, outputs, and comparison.
- Hash preserved artefacts when feasible. A hash supports integrity checking; it does not prove that an artefact is truthful or complete.
- Do not store secrets or unnecessary personal data in public logs.

## Required batch fields

| Field | Meaning |
|---|---|
| `schema_version` | Version of this basic format |
| `batch_id` | Unique identifier for this batch attempt |
| `purpose` | Question or behaviour being examined |
| `specification_ref` | Frozen test plan and version/hash |
| `condition` | Declared condition, e.g. A, B, control, treatment |
| `started_at`, `ended_at` | Timestamps with timezone; null if unknown |
| `executor` | System, agent, software, or person executing |
| `environment` | Relevant environment and reset/isolation facts |
| `inputs` | Input references and hashes where practical |
| `resources` | Relevant files, instructions, libraries, versions, and hashes |
| `procedure` | Steps, commands, prompts, or procedure reference |
| `status` | `completed`, `failed`, `incomplete`, or `invalid` |
| `events` | Ordered event records, including errors and omissions |
| `outputs` | Output/artifact references, media type, and hash where available |
| `deviations` | Differences from the frozen plan |
| `limitations` | Missing evidence and known interpretive limits |
| `provenance` | Collector, collection time, and integrity metadata |
| `interpretation` | Optional; explicitly separate from observed facts |

## Event record

Each event should have, where applicable:

- `event_id`: stable within the batch;
- `sequence`: monotonically increasing order;
- `timestamp`: timestamp with timezone;
- `type`: e.g. `start`, `action`, `response`, `assertion`, `warning`, `error`, `timeout`, `artifact_written`, `collection_gap`, `end`;
- `actor`: who or what produced/observed the event;
- `action` and `observation`: what was attempted and what was actually observed;
- `status`: outcome of that event;
- `evidence_refs`: references to raw logs or artefacts;
- `notes`: optional contextual information.

Do not force every domain into the same event vocabulary. Preserve the core fields and allow specialized event types.

## Minimal JSON shape

```json
{
  "schema_version": "basic-evidence-log/0.1",
  "batch_id": "demo-A-001",
  "purpose": "Check whether comment-only code changes alter test outcomes",
  "specification_ref": "examples/generic_ab/PLAN.md",
  "condition": "A",
  "started_at": null,
  "ended_at": null,
  "executor": {"name": "example-runner", "version": "1.0"},
  "environment": {"os": "record-at-run-time", "reset": "fresh process; filesystem state declared"},
  "inputs": [],
  "resources": [],
  "procedure": ["Run the declared test command"],
  "status": "incomplete",
  "events": [],
  "outputs": [],
  "deviations": [],
  "limitations": ["Example template; not a record of a real execution"],
  "provenance": {"collector": "example", "collected_at": null},
  "interpretation": null
}
```

## Specialized formats

A derived format must:
1. name the basic schema version it extends;
2. retain all applicable basic fields without changing their meaning;
3. add domain-specific fields in a clearly named section;
4. record its own schema version;
5. define its own acceptance and validation rules;
6. preserve raw source evidence and distinguish it from generated summaries.

See the AEL runtime repository's software-testing extension for an applied example.

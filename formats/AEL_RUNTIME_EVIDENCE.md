# AEL Runtime Evidence Extension

**Schema:** `qbatch-ael-runtime-evidence/0.1`  
**Extends:** Basic Evidence Log Format `basic-evidence-log/0.1`  
**Optional companion:** Software-Testing Log Format `qbatch-software-test-log/0.1`

This extension joins Q-Batch's portable experiment record to AEL's runtime event ledger and separate audit sidecar. It is a proposed evidence contract, not a claim that every field is already emitted automatically by the runtime.

## Separation of concerns

Keep three records distinct and link them by stable IDs:

1. **AEL event ledger:** what the runtime recorded as events and decisions. It remains append-only.
2. **Runtime audit sidecar:** how the active context was assembled, including included/omitted event IDs, scope, hashes, and budget diagnostics. It must not be passed to the model.
3. **Q-Batch evidence record:** the frozen test conditions, raw artifacts, collection status, deviations, and later interpretation.

The model-facing input is a fourth, deliberately smaller object. For the current adapter it contains only `working_context` and `current_user_message` (plus the fixed runtime instruction and selected local model name in the request wrapper). Do not copy audit-sidecar content into model input for convenience.

## Additional fields

Retain all applicable fields from the basic record. Add the following top-level `ael_runtime` object:

| Field | Meaning |
|---|---|
| `runtime_version` | Release/tag or source revision actually tested |
| `runtime_source_sha` | Commit or immutable source identifier |
| `ledger_ref` | Reference to the database snapshot or exported ledger evidence; include a hash for exported files |
| `ledger_high_watermark` | Last event sequence/position included in the evidence snapshot, if known |
| `audit_sidecar_ref` | Path/reference and SHA-256 for the runtime audit sidecar |
| `model_input_ref` | Path/reference and SHA-256 for the exact model-facing input, if one was constructed |
| `response_ref` | Path/reference and SHA-256 for the raw response, if a response was produced |
| `model_call` | Provider/adapter, model identifier, endpoint class (e.g. loopback), and whether inference was real, mocked, or not attempted |
| `boundary_checks` | Expected vs observed results for model-input allowlist and audit separation |
| `failure_point` | Named stage where execution stopped, or null |
| `recovery` | Whether a retry/recovery was attempted and its relationship to the original attempt |

Do not put secrets, credentials, full private prompts, unnecessary personal data, or raw private content into public records. Public evidence can use redacted references and hashes; keep access-controlled source artifacts elsewhere.

## Runtime event linkage

For each event relevant to the tested claim, preserve a reference to the source ledger event rather than paraphrasing it as if it were raw evidence. Where a portable export is used, retain these AEL event attributes when present:

- event ID and sequence;
- creation timestamp;
- event type;
- provenance, decision authority, inference kind, and truth status as separate fields;
- source reference, branch/strategy identifiers when applicable;
- content or a privacy-safe artifact reference;
- metadata reference/hash where useful.

Do not collapse provenance, authority, inference kind, and truth status into one label. Missing values stay unknown; do not infer a successful event from the absence of an error.

## Failure and incomplete-run rules

- Create one evidence record per execution attempt. A retry gets a new `batch_id` and links to the earlier attempt.
- If the process fails before starting, record `status: "failed"`, the observed failure stage, and null exit code if none was captured.
- If collection fails after execution, record the execution result separately from evidence-collection status. Do not silently label the whole record complete.
- A missing response is not an empty response. A missing audit file is not proof that no audit data existed.
- Keep raw stdout/stderr, response, audit, and exported ledger artifacts unchanged; derived summaries reference them.
- Distinguish observed facts from interpretation. A mock-server pass validates the mock integration path, not real model inference.
- If a failure is repaired, preserve the failed attempt and make the repair/retry a new record.

## Reconstruction acceptance checklist

A reviewer who did not witness the run should be able to answer from the preserved evidence alone:

1. What exact runtime revision and test specification were used?
2. What inputs, resources, environment, and reset assumptions applied?
3. Did execution start, and where did it stop or complete?
4. Which ledger events and audit sidecar belong to this attempt?
5. What exactly was sent to the model, if anything, and what came back?
6. Which raw artifacts support the reported exit code, test counts, and boundary checks?
7. What is unknown, missing, mocked, or otherwise limiting the conclusion?

If a required answer cannot be reconstructed, mark the record incomplete or the relevant check unverifiable. Do not fill gaps from recollection.

## Minimal example shape

See [failed-run-template.json](../examples/ael_runtime/failed-run-template.json). It is a synthetic template for validating the schema and reconstruction workflow, not evidence of an actual AEL runtime failure.

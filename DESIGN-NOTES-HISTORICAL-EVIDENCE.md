# Q-Batch Design Notes: Historical Evidence and Related Software

**Status:** Discussion record, 2026-10-28 to 2026-10-29  
**Purpose:** Preserve the design discussion and decisions so they do not depend on conversational context.  
**Relationship to the specification:** This records rationale, boundaries, and open design requirements. It does not silently replace or claim implementation of the Q-Batch specification.

## 1. The problem Q-Batch addresses

Q-Batch is not an attempt to replace conventional A/B testing. It addresses cases where back-to-back comparisons are too heavy, brittle, or confounded by carryover, order, timing, prior exposure, shared state, or resource-loading differences.

The core method remains:

**Specify → run independently → preserve evidence → compare offline.**

The batches need not run together, on the same day, in the same account, or with the same agent. Each batch must carry enough context to interpret its results without relying on memory of the original runtime.

The longer-term historical evidence archive is a major part of the idea, not merely a side effect of running an A/B test. It should allow evidence from independent runs to remain useful, inspectable, and comparable over time.

## 2. Historical evidence requirements

The archive should preserve individual evidence-producing attempts, including failed and incomplete attempts. A failed run is not a successful result, but it is still part of the test history and may explain later changes.

Historical records need, at minimum, to support:

- **Stable identity:** distinct identities for the test/specification, batch, run/attempt, and evidence artefacts.
- **Origin and lineage:** source repository, branch/commit or equivalent source revision, test-suite/specification version, and links between an attempt and its parent, retry, or recovery change where applicable.
- **Declared conditions:** agent/system and version, environment, reset/isolation procedure and limitations, resources/instructions/includes loaded, configuration, inputs, and relevant external dependencies.
- **Observed evidence:** actual responses, event logs, commands and results where available, errors, warnings, omissions, and required artefacts. A claim that work occurred is not a substitute for captured evidence that it occurred.
- **Integrity and provenance:** evidence location, hashes or equivalent integrity references where useful, collection method, and an account of any post-collection alteration. Preserve originals when creating redacted or derived copies.
- **Lifecycle:** status (completed, failed, invalid, incomplete, or pending), deviations, failure reason, retry/recovery links, and what changed between attempts. Never silently overwrite a failed attempt with a later success or merge evidence from separate attempts.
- **Comparability:** explicit specification and condition versions, so a comparison can disclose when two runs are not equivalent.
- **Queryability and longevity:** records should remain discoverable and interpretable after the original process, chat, runner, branch, or service is gone.
- **Evidence-to-conclusion traceability:** a later finding must point back to the evidence and criteria that support it; observations must remain distinguishable from interpretations.

These are requirements for the record system to support. They do not imply that every field must be mandatory for every kind of test, or that all fields need to live in one enormous log file.

## 3. Keep the responsibilities separate

The discussion established four distinct responsibilities:

1. **Event/evidence logging — capture.** Record what happened, what was observed, where the evidence came from, and how to verify or retrieve it.
2. **Comparison and post-processing — interpretation.** Compare batches against predeclared expectations and criteria, preserve differences and missing evidence, and state what can and cannot be concluded.
3. **Historical archive — continuity.** Preserve immutable run/attempt records, versioned context, lineage, failures, retries, and later corrections or derived analyses.
4. **Evidence review — scrutiny.** Q-Batch should support a basic evidence review without requiring a separate Peer Review skill. Peer Review is optional for deeper or multi-reviewer analysis; it does not replace batch records or the comparison record.

**The event log must not own comparative analysis.** It records events, evidence, and provenance. It must not embed averages, aggregate scores, or post-processing assumptions that erase raw distinctions. Allure-style averages were specifically considered unacceptable for the evidence layer: retain raw detail and make any aggregation an explicit, separately inspectable analysis.

A historical archive may index or reference evidence and analyses, but it should not rewrite the original observations to fit a later interpretation.

## 4. Related software discussed

The purpose of looking at existing software is to identify reusable mechanisms and design lessons, not to copy a whole product or make Q-Batch dependent on a large platform.

| Software / project | Relevant area discussed | Design lesson for Q-Batch |
|---|---|---|
| [Allure Report](https://allurereport.org/) | Test reporting and summaries | Reporting can help inspection, but aggregate/average views must not replace raw event and evidence detail. |
| [ReportPortal](https://reportportal.io/) | Test-result aggregation and analysis | Consider useful mechanisms for organizing and examining test results; keep analysis separate from original evidence. |
| [Buildkite Test Analytics](https://buildkite.com/resources/) | Test history and test analytics | Historical trends and test/run history are relevant capabilities to study; do not assume their product model is the archive design. |
| [OpenTelemetry](https://opentelemetry.io/) | Structured events, traces, context and observability conventions | Borrow useful ideas for event identity, context, correlation, and traceability where they fit; Q-Batch does not need to become an observability platform. |
| [OpenLineage](https://openlineage.io/) | Lineage and provenance | Consider how to link outputs to the jobs, inputs, and versions that produced them. |
| [Apache Parquet](https://parquet.apache.org/) | Durable analytical data format | A possible later storage/export option for large-scale analysis, not a required log format or an immediate dependency. |
| [DuckDB](https://duckdb.org/) | Local analytical queries over retained data | Potentially useful if archive queries outgrow simple files and Python; not required to start. |
| [Grafana](https://grafana.com/) | Querying and visualizing historical telemetry | Dashboards may be useful downstream, but visualization is not the source of truth and is not a prerequisite. |

This is a record of the comparison directions and design implications discussed, not a claim that every product has been exhaustively benchmarked or that any of them has been selected as a dependency. Product-specific capabilities should be verified against current documentation before implementation decisions rely on them.

## 5. Implementation constraints and non-goals

- Start with simple, inspectable files and Python. **DuckDB is not a prerequisite.**
- Reuse individual mechanisms or conventions when they solve a demonstrated problem; do not recreate the full architecture of Allure, ReportPortal, Buildkite, OpenTelemetry, or Grafana.
- Do not turn the event logger into a comparison engine, or the comparison report into the historical source of truth.
- Do not assume that a new chat/process/account proves environmental independence. Record the reset method and its limits.
- Do not silently rewrite old evidence after changing a specification, test, model, resource, or evaluation criterion. Version the change and disclose cross-version comparisons.
- Do not treat one pair of runs, a passing instrumentation test, or a synthetic demonstration as proof of general test or model effectiveness.
- Do not require Peer Review for every Q-Batch. Basic evidence review is part of the method; the Peer Review skill is an optional extension.

## 6. Relationship to AEL and software A/B tests

The AEL runtime accountability experiment is one possible consumer of Q-Batch principles, not the definition of Q-Batch itself. Its runner, model protocol, tool-call handling, and test task are implementation-specific.

A generic software A/B fixture is useful for testing whether batch records and comparison procedures work. A synthetic fixture can verify mechanics, but cannot establish that a Critical Thinking skill or any other system improves performance.

For every real experiment, preserve its failed/incomplete attempts as distinct records, link recovery changes to them, and score only evidence that passes the declared validity criteria.

## 7. Open questions — not decisions

These questions require evidence or practical use before being settled:

- Which fields should be mandatory for every batch type versus conditionally required?
- What is the lightest useful storage/indexing approach once the archive contains many batches?
- Which lineage and event conventions from existing projects are worth adopting directly?
- How should retention, export, integrity verification, and archive migration work at larger scale?
- Which comparison operations are generic enough to standardize without constraining different test types?

Resolve these from actual use and evidence. Do not add dependencies, folders, or a more elaborate schema merely because a tool or pattern exists.

## 8. Decision summary

- Q-Batch complements A/B testing; it is especially useful when independent execution and offline comparison reduce carryover or coordination problems.
- Longitudinal historical evidence is a central value of the project.
- Preserve raw observations and provenance; keep comparison, historical lifecycle, and review responsibilities distinct.
- Preserve failures and retries rather than overwriting history.
- Basic evidence review is required; Peer Review is optional.
- Borrow mechanisms from related software, not entire products.
- Python and simple files are sufficient to begin; DuckDB and analytical platforms are optional future choices.

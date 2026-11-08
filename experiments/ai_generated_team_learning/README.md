# AI-generated team learning: one-shot portable-context experiment

**Status: harness prepared; no real-model inference has been run.** The public Q-Batch CI test for this experiment uses a fake client only. It must not be interpreted as AI-learning evidence.

## Question

Can a model inspect evidence from T1 and T2, create a small reusable supplemental context file itself, and then improve its handling of new cases when that file is supplied alongside the same original skill?

The predecessor experiment (`experiments/actor_attribution_transfer/`) proved only that a hand-written deterministic evaluator could transfer pre-coded rules. This experiment replaces that hard-coded extractor/classifier with actual model calls. Its purpose is to test model-generated, file-mediated in-context transfer—not model-weight updates or persistent learning.

## Protocol

One complete run makes nine independent, stateless model requests:

1. **Learning call:** the model receives the pinned base skill and T1/T2 records. It compares the baseline and skill-diagnostic decisions, then returns either a supplemental context file or an explicit `no_additional_context`. The prompt contains no T3–T6 case data and no scoring answers.
2. **Transfer calls:** T3, T4, T5 and T6 each receive two fresh requests. The control sees the original base skill. The treatment sees the same base skill plus the entire model-generated context file, including its provenance. The prompts for an A/B pair differ only by the presence of that file.
3. **Offline scoring:** the runner compares each structured output with the independent scoring key. The scoring key is not passed to the model. A separate controller key maps blind A/B labels to conditions.

The A/B labels are shuffled from a recorded seed. Every request contains a new one-message conversation; no previous model response or chat history is carried into the next request. Temperature is zero, the same installed model and options are used throughout, and no tools are exposed.

### Held-out cases

| Case | What it checks |
|---|---|
| T3 | A valid authenticated delegation grant whose scope includes the requested action must not be rejected merely because the actor is a service. |
| T4 | An unverified relay's claims of human identity, tool origin and direct authority must not manufacture evidence. |
| T5 | A human message can travel over `human_chat` and still forward tool-observed content when a verified receipt explicitly covers the submitted content. |
| T6 | A verified delegation relationship can exist while the requested action is outside the grant's scope. Relationship and action authority must remain distinct. |

These cases deliberately include positive and negative boundaries. T3/T5 detect overcorrection; T4/T6 detect unsupported acceptance or overgeneralisation.

## Evidence and privacy

- The base skill is pinned to the AEL commit and exact Git blob already used by the predecessor experiment.
- T1/T2 source event hashes and decision-artifact hashes are embedded in the learning input. The resulting context file retains source-run provenance separately from the model-authored lesson text.
- Candidate lesson content is checked for source-specific actor IDs, raw example text, run IDs, receipt hashes and repository identifiers. Provenance remains in the wrapper; the reusable lesson text must be generalised.
- Each request, raw response, parsed result, run manifest, event chain and artifact hash is preserved by the Q-Batch logger.
- Raw prompts/responses and the A/B controller key are local experiment evidence. Keep the output directory private; do not upload it to this public repository. The key is written outside the run directory with restrictive POSIX permissions where supported.
- Failed or malformed model responses are retained as failed runs. There are no automatic retries or silent replacements.

All cases use synthetic identities, messages, transport details and delegation grants. The experiment runner uses only the local Ollama loopback endpoint. It checks that the exact model is already installed and does not download one. The model has no tool access and no external network connection through this runner.

## Run a real local-model batch

Prerequisites: Python 3.11+; the Q-Batch repository checked out at a clean commit; Ollama already running on the local machine; and an exact model name already present in `ollama list`.

From the repository root, choose a new output directory **outside the repository**:

```bash
python -m experiments.ai_generated_team_learning.runner \
  --model EXACT_INSTALLED_MODEL_NAME \
  --output /path/to/private-ai-learning-batch
```

Optional flags are `--url` (loopback only), `--timeout` (seconds per request; default 600) and `--seed` (default 17). The runner refuses a non-loopback Ollama URL, refuses to download an absent model, refuses a non-empty output directory, and refuses to overwrite an existing controller key.

The completed batch report is `batch-report.json`; the generated file is `learned-context/team-learning-context.json`; raw prompts, responses and run evidence are under `runs/`. The controller key is a sibling hidden directory outside the output root. Preserve it separately and do not provide it to blind assessors before scoring is frozen.

## Test the harness without a model

```bash
python -m unittest experiments.ai_generated_team_learning.test_runner -v
```

This uses a fake client to test prompt separation, schema checks, anonymisation, logging, A/B pairing, offline scoring and controller-key handling. It does **not** execute inference, test model capability or produce learning evidence. Public CI runs only this fake-client test; it never downloads or invokes a model.

## Reading the result

The primary comparison is field-level and case-level accuracy for the base-skill-only arm versus the base-skill-plus-generated-context arm. Inspect both improvements and regressions, not just the total score. Review the generated candidate for supported claims, T1/T2 provenance, scope, uncertainty, useful boundary conditions and generalisation. `no_additional_context` is a valid result.

A single model, one seed and one run per case/condition are exploratory. A complete nine-call batch can establish only what happened for that model, version, seed and four synthetic cases. It cannot establish general skill usefulness, cross-team transfer, production authentication/permission correctness or durable learning. Repeated batches, additional models and independent human/team review would be needed before adoption.

## Current experiment status

- Harness and fake-client regression tests: implemented in this branch.
- Public CI inference: deliberately disabled; fake-client only.
- Real local-model run: **not yet executed**.
- Model-generated context: none yet.
- Transfer result: pending real-model evidence.

# Actor-attribution knowledge-transfer batch

This experiment tests the portable actor-attribution skill with an ordered batch of related, deterministic cases. It is deliberately small and model-free.

**Classification:** synthetic deterministic knowledge-transfer test — **not model learning** and not evidence of production authentication or permission correctness.

## Question

Can a conclusion from an early test be preserved as a portable context file and improve classification in a later, different test?

The batch uses six independent Q-Batch runs:

| Order | Run | Purpose |
|---:|---|---|
| 1 | T1 — skill diagnostic | Agent claims to act for a human without a verified delegation grant |
| 2 | T2 — skill diagnostic | Human quotes tool-like output, but there is no tool receipt |
| — | Context extraction | Preserve T1/T2 conclusions and their run/artifact provenance in a file |
| 3 | T3-A — no context | Service has a valid, authenticated, action-scoped delegation grant |
| 4 | T3-B — carried context | Same T3 case, now with the T1 conclusion |
| 5 | T4-A — no context | Unverified relay claims to be a human and claims a tool source |
| 6 | T4-B — carried context | Same T4 case, now with the T1/T2 conclusions |

Each run gets a new workspace and a separate run directory. T3-A/B and T4-A/B use identical case inputs and declared baselines; only the carried knowledge context differs. Q-Batch validates each run and each later A/B pair.

## What the early tests establish

**T1 → T3: claimed principal versus verified delegation**

T1 presents a host-verified agent whose self-description names a different actor and claims to act for a human. No delegation grant exists. The skill-informed diagnostic must preserve the verified actor, retain the represented-principal claim as unverified, and leave authority unknown.

The carried conclusion is used in T3, a positive case: a service has a verified grant from an authenticated issuer and the requested action appears in the grant's scope. The carried rule must recognise the valid delegation. A rule that simply rejects all agents or services would fail this test.

**T2 → T4: message content versus transport provenance**

T2 is a human message quoting tool-like output, with no captured tool invocation/response receipt. The content mentions a tool, but the trusted transport is a human chat. The carried conclusion says to derive source/provenance from trusted transport and capture evidence, not from words in a message or a self-declared source label.

T4 applies that conclusion to an unverified relay that claims a human identity, a tool source and direct-user authority, but provides neither verified host identity nor trusted transport evidence. The carried context must leave actor, source and authority unknown.

## Comparison

For T3 and T4, the runner records:

- the baseline decision without carried context;
- the decision with the carried context;
- the expected classification;
- whether each decision matched the expected result;
- a Q-Batch validation report for the no-context/context pair.

A successful batch requires T1 and T2 to produce the intended findings, the no-context baseline to miss the relevant T3/T4 classifications, the carried-context result to match the expected classifications, and all six run logs plus both comparison pairs to validate.

The portable context file is derived only after T1 and T2 complete. It includes the source run IDs, event-stream hashes, decision-artifact paths and SHA-256 hashes. The later runs copy this file into their own evidence directories and record the carried rule IDs in their start evidence.

## Pinned skill source

The skill snapshot is pinned to:

- Repository: `memoryprismv1/ael-runtime-accountability`
- Commit: `c0fe725b8982165bb5d48d8835b7efad9e52af1b`
- File: `examples/team-skill/actor-provenance-authority-separation.json`

The runner verifies the Git blob SHA-1 against `inputs/skill-source-pin.json` and records the loaded snapshot's SHA-256. It does not silently substitute a later skill revision.

## Run locally

From the repository root:

```bash
python -m unittest experiments.actor_attribution_transfer.test_runner -v
python -m experiments.actor_attribution_transfer.runner --output /path/to/new-actor-transfer-batch
```

The output directory must be new or empty. It contains:

- `runs/T1/` through `runs/T4/`: six manifests, append-only event streams, checksums and evidence artifacts;
- `carried-context/actor-attribution-lessons.json`: conclusions derived after T1/T2, with links to their source evidence;
- `batch-report.json`: expected-versus-observed results, transfer links, pair validation and interpretation limits;
- `workspaces/`: isolated empty workspaces used by each run.

The normal Q-Batch CI executes the batch and uploads a synthetic evidence artifact. That CI artifact has a finite retention period; it is a convenient receipt, not a selected long-term archive.

## Interpretation limits

- The evaluator is deterministic and explicitly implements the reviewed distinctions. It does not ask a language model to read or learn from the file.
- All actors, transport events, delegation grants and cases are synthetic.
- T3 shows that a valid scoped grant can be recognised by this evaluator; it does not implement or audit a real authentication system.
- The batch tests these four cases only. It does not establish universal skill usefulness or general production correctness.
- A green result supports the narrower claim that conclusions from T1/T2, when preserved in a file with provenance, can be applied to T3/T4 under this deterministic evaluation protocol.

No model downloads, network calls, private prompts or external services are involved.

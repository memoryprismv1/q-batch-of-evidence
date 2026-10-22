# Q-Batch Specification

**Status:** Initial working specification  
**Method:** Q-Batch of Evidence  
**Version:** 0.1

## 1. Purpose

Q-Batch is a method for running independently specified test batches and comparing their preserved outputs outside the test runtime.

It is useful when sequential exposure can contaminate a later test, when batches need different resource sets, or when execution and review cannot conveniently happen together.

## 2. Core sequence

### 2.1 Define expectations before execution

Before a batch runs, record:

- the question or behaviour being tested;
- the expected response, logs, results, and required artefacts;
- the resources, libraries, includes, instructions, and versions permitted for that batch;
- the environment and reset conditions required;
- the collection method and any known limitations.

Do not redefine success after seeing the result without recording that change as a new or revised specification.

### 2.2 Run each batch independently

For each batch:

1. Establish the declared environment and load its specified resources.
2. Run the defined test procedure.
3. Collect the actual responses, logs, results, and required artefacts.
4. Record deviations, errors, omissions, and environmental facts that could affect interpretation.
5. Preserve the batch output as a distinct, identifiable evidence set.

A batch can contain one test or many. Keep test identity and output identity clear enough to trace each result back to its inputs.

### 2.3 Compare offline

Once the relevant evidence sets are available, compare them outside the execution contexts.

The comparison should address:

- whether each batch met its own declared expectations;
- which outputs agree or differ;
- missing, malformed, or unexpected evidence;
- whether differences are consistent with the declared resource or environment differences;
- unresolved ambiguity and limits on the conclusions.

The comparison process should use the preserved evidence and evaluation criteria. It should not silently rerun the tests or rely on undocumented recollection of the original runtime.

## 3. Batch independence and timing

Batch A and Batch B:

- may run on different days and in either order;
- need not run consecutively or simultaneously;
- may use different agents, accounts, resource libraries, includes, or loading conditions;
- must have their conditions recorded well enough to interpret their results.

Identical conditions are not mandatory. The important requirement is that the conditions and intended comparison are explicit.

## 4. Environment reset and contamination

A fresh conversation, process, or account does not automatically prove a fully reset environment. Depending on the system, persistent memory, cached artefacts, shared files, external state, prior exposure, or other hidden context may remain.

Record the reset method and what it does and does not cover. Use separate environments or other isolation measures where the test requires them. If complete isolation cannot be established, state that limitation rather than claiming a clean run.

## 5. Minimum evidence record

Use a separate record for each batch. The fields below are a practical minimum, not a required file format.

| Field | What to record |
|---|---|
| Batch ID | Stable identifier, such as A or B plus a run identifier |
| Test/specification version | The expectations and procedure used |
| Run time | When the batch ran; include timezone where relevant |
| Agent/system | Model, software, service, or runner, including version if known |
| Environment/reset | Account or environment identifier suitable for the project, reset procedure, known persistence |
| Resources loaded | Libraries, files, includes, instructions, versions, and relevant hashes where useful |
| Procedure | Commands, prompts, inputs, and sequence needed to understand the run |
| Responses | Actual outputs, preserved without silent editing |
| Logs/results | Runtime logs, result files, status, errors, and warnings |
| Deviations | Anything that departed from the declared setup or expected collection |
| Artefact references | Paths or links to the preserved evidence |
| Limitations | Missing information or uncertainties affecting interpretation |

Avoid recording secrets or unnecessary personal data in public artefacts.

## 6. Comparison record

The offline comparison should identify:

- the evidence sets compared and their specification versions;
- the criteria used;
- expected versus observed results for each batch;
- differences, omissions, and unexpected outputs;
- any conclusion and the evidence supporting it;
- limitations, confounds, or questions left open;
- the identity/version of the comparison procedure, if relevant.

Keep observations distinct from interpretations. A difference between batches is evidence of a difference, not automatically proof of its cause.

## 7. Changes to the test

If expectations, resources, procedures, or evaluation criteria change, record the change and version it. Do not overwrite an earlier evidence set in a way that obscures the conditions under which it was produced.

A new batch can use an updated specification, but comparisons across specification versions must disclose that fact.

## 8. What Q-Batch is not

Q-Batch is not a claim that all environmental contamination can be eliminated, nor does it prescribe a particular test runner, file format, agent, or continuous-integration system. It is a method for separating specified execution from evidence-based comparison.

It is not inherently an A/B test. It can be used for comparisons, but it can also check each batch against its own expectations, including when batches use different resources.

## 9. Short form

**Specify → run independently → preserve evidence → compare offline.**

The evidence should outlive the runtime that produced it.

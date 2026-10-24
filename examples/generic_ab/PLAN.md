# Generic A/B Demonstration Plan

**Purpose:** Exercise Q-Batch evidence capture with a deliberately simple software-testing example. This is a methodology demonstration, not a claim about AEL efficacy.

## Question

Do two source branches that differ only by comments produce the same results under the same small test procedure?

## Conditions

- **A (baseline):** the original fixture.
- **B (comment-only variant):** a branch created from A; the only intended source change is adding comments.
- Same interpreter, test command, inputs, and acceptance criteria for both.
- Run each condition in a separate fresh process and preserve each output independently.

## Fixture

`fixture.py` exposes `classify_count(value)`, returning `"empty"` for zero, `"single"` for one, and `"multiple"` otherwise. The test suite checks representative values and records actual results.

## Predeclared expectations

1. Both conditions pass the same test suite.
2. The executable behaviour is identical for the declared test inputs.
3. The source diff from A to B contains comments only.
4. Each batch has a separate basic evidence log and specialized software-test log.
5. Logs point to exact source revisions, commands, exit codes, test output and artifact hashes.
6. The offline comparison states whether the evidence supports equivalence for this fixture and these inputs only.

## What this does not prove

- It is not a statistical or user-facing A/B experiment.
- It does not prove equivalence for all possible inputs or environments.
- Matching test outcomes alone do not prove the source diff was comment-only; inspect the diff as separate evidence.
- Example records must not be labelled as real runs until the commands have actually been executed and the observed outputs collected.

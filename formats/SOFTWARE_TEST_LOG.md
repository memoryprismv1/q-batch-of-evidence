# Software-Testing Log Format

**Schema:** `qbatch-software-test-log/0.1`  
**Extends:** Basic Evidence Log Format `basic-evidence-log/0.1`

This is a domain-specific extension, not a replacement for the basic log. Keep all applicable basic fields and meanings.

## Additional fields

| Field | Meaning |
|---|---|
| `source_revision` | Exact commit/revision tested |
| `source_diff_ref` | Diff against declared baseline; include hash |
| `runtime` | Language/runtime and version |
| `dependency_lock_ref` | Dependency lockfile and hash, or explicit none |
| `test_command` | Exact command executed |
| `working_directory` | Directory from which the command ran |
| `test_framework` | Framework and version, if any |
| `exit_code` | Observed process exit code; null if not captured |
| `test_counts` | Passed, failed, skipped, errors, collected |
| `assertions` | Expected vs observed outcomes and test identifiers |
| `stdout_ref`, `stderr_ref` | Raw output references and hashes |
| `coverage_ref` | Optional coverage report and hash |
| `changed_files` | Exact changed paths and diff/hash |
| `acceptance_result` | `pass`, `fail`, `incomplete`, or `not_run` |
| `validation_result` | Whether log and artifact validation passed, with reasons |

## Minimum collection sequence

1. Record the batch manifest and source revision before execution.
2. Capture the exact command, runtime, working directory, and dependency state.
3. Capture stdout, stderr, exit code, and test report without editing the raw outputs.
4. Hash the source diff and collected outputs.
5. Record test counts and acceptance outcome from observed runner output—not model self-report.
6. Validate required fields and artifact references.
7. Freeze the batch record and raw artifacts together.
8. Compare A and B offline using the predeclared plan.

## Example shape

```json
{
  "schema_version": "qbatch-software-test-log/0.1",
  "extends": "basic-evidence-log/0.1",
  "software_test": {
    "source_revision": null,
    "source_diff_ref": null,
    "runtime": null,
    "dependency_lock_ref": null,
    "test_command": "python -m unittest -v test_fixture.py",
    "working_directory": null,
    "test_framework": "unittest",
    "exit_code": null,
    "test_counts": {"passed": null, "failed": null, "skipped": null, "errors": null, "collected": null},
    "assertions": [],
    "stdout_ref": null,
    "stderr_ref": null,
    "coverage_ref": null,
    "changed_files": [],
    "acceptance_result": "not_run",
    "validation_result": {"status": "not_run", "reasons": []}
  }
}
```

Null values mean unknown or not captured, not zero. If the process never starts, record that fact and leave the exit code null. If test execution is interrupted, do not label it a pass or a complete run.

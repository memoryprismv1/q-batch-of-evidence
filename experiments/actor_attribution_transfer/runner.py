"""Deterministic Q-Batch experiment for cross-test actor-attribution knowledge transfer.

T1/T2 apply the pinned portable skill and generate findings. Those findings are
preserved with source-run hashes, then carried into T3/T4. Each later case runs
both without and with the carried context. No model or external service is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

from experiments.ct_ab.context import load_context
from experiments.ct_ab.logger import (
    LOGGER_VERSION, SCHEMA_VERSION, RunLogger, canonical_json,
    sha256_bytes, utc_now,
)
from experiments.ct_ab.validate_log import validate_pair, validate_run

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INPUTS = PACKAGE / "inputs"
CASEBOOK_PATH = PACKAGE / "cases.json"
SKILL_PATH = INPUTS / "actor-attribution-portable-skill.json"
PIN_PATH = INPUTS / "skill-source-pin.json"
CONTEXT_ID = "qbatch-actor-attribution-transfer-v1"
BASE_COMMIT = "actor-attribution-transfer-fixture-v1"
MODEL = {"provider": "deterministic-policy-evaluator", "model_id": "actor-attribution-evaluator-v1"}
ENVIRONMENT = {"execution": "local-python", "network": False, "model_inference": False}
RESOURCE_LIMITS = {"model_calls": 0, "external_services": 0, "max_runs": 6}

RULE_PRINCIPAL = "separate_claimed_principal_from_verified_authority"
RULE_PROVENANCE = "derive_provenance_from_trusted_transport"


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"


def _sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}".encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def _load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    casebook = json.loads(CASEBOOK_PATH.read_text(encoding="utf-8"))
    skill_bytes = SKILL_PATH.read_bytes()
    skill = json.loads(skill_bytes)
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    actual_blob = _git_blob_sha1(skill_bytes)
    if actual_blob != pin["source_blob_sha1"]:
        raise ValueError(
            "portable skill snapshot does not match the pinned AEL Git blob: "
            f"expected {pin['source_blob_sha1']}, got {actual_blob}"
        )
    if skill.get("skill_id") != "separate-actor-identity-classification-and-authority":
        raise ValueError("unexpected portable skill ID")
    return casebook, skill, pin, sha256_bytes(skill_bytes)


def _rules_from_skill(skill: Mapping[str, Any]) -> set[str]:
    """Map the reviewed skill's actual method text to this fixture's rule IDs."""
    steps = " ".join(item["action"].casefold() for item in skill["generalised_method"])
    rules: set[str] = set()
    if (
        "authority separately" in steps
        and "delegation evidence" in steps
        and "acting agent or service distinct" in steps
    ):
        rules.add(RULE_PRINCIPAL)
    if "transport or source metadata" in steps and "how an event entered the system" in steps:
        rules.add(RULE_PROVENANCE)
    required = {RULE_PRINCIPAL, RULE_PROVENANCE}
    if not required.issubset(rules):
        raise ValueError(f"pinned skill does not contain required reviewed method rules: {sorted(required - rules)}")
    return rules


def legacy_decision(case: Mapping[str, Any]) -> dict[str, Any]:
    """A deliberately naive self-description-first baseline, not an AEL policy."""
    claims = case.get("self_asserted_claims", {})
    host = case.get("host_identity", {})
    actor_type = claims.get("actor_type") or host.get("actor_type") or "human"
    actor_id = claims.get("actor_id") or host.get("actor_id")
    source = claims.get("source") or (
        case.get("trusted_transport", {}).get("source")
        if case.get("trusted_transport", {}).get("verified") else "unknown"
    )
    authority = claims.get("authority")
    if authority is None:
        authority = "user_direct" if actor_type == "human" else "none"
    return {
        "actor_type": actor_type,
        "actor_id": actor_id,
        "source": source or "unknown",
        "principal_status": "accepted_claim" if claims.get("on_behalf_of") else "not_claimed",
        "authority": authority,
        "content_origin": "tool_observed" if source == "tool_output" else "message_content",
        "claimed_source_status": "accepted_self_description" if claims.get("source") else "not_claimed",
        "policy": "legacy_self_description_first",
    }


def evidence_based_decision(case: Mapping[str, Any], rules: set[str]) -> dict[str, Any]:
    """Apply only the transferable distinctions present in the carried rules."""
    claims = case.get("self_asserted_claims", {})
    host = case.get("host_identity", {})
    transport = case.get("trusted_transport", {})
    action = case.get("action", "")
    actor_rule = RULE_PRINCIPAL in rules
    provenance_rule = RULE_PROVENANCE in rules

    if actor_rule:
        if host.get("verified") is True and host.get("actor_id") and host.get("actor_type"):
            actor_type, actor_id = host["actor_type"], host["actor_id"]
        else:
            actor_type, actor_id = "unknown", None
    else:
        actor_type, actor_id = legacy_decision(case)["actor_type"], legacy_decision(case)["actor_id"]

    if provenance_rule:
        source = transport.get("source") if transport.get("verified") is True else "unknown"
    else:
        source = legacy_decision(case)["source"]

    grant = case.get("delegation_evidence") or {}
    grant_verified = (
        actor_rule
        and grant.get("verified") is True
        and grant.get("issuer_authenticated") is True
        and bool(grant.get("grant_id"))
        and bool(grant.get("principal_id"))
        and action in grant.get("scopes", [])
    )
    on_behalf_claim = claims.get("on_behalf_of")
    if grant_verified:
        principal_status = "verified_delegation"
        authority = "delegated_authority_verified"
        principal_id = grant["principal_id"]
    elif on_behalf_claim:
        principal_status = "unverified_claim"
        authority = "unknown"
        principal_id = on_behalf_claim
    else:
        principal_status = "not_claimed"
        authority = "unknown"
        principal_id = None

    tool_capture = case.get("tool_capture") or {}
    claimed_source = claims.get("source")
    if provenance_rule and claimed_source == "tool_output":
        if source == "human_chat" and tool_capture.get("present") is not True:
            content_origin = "human_submitted_statement"
            claimed_source_status = "unverified_not_tool_observed"
        elif source == "tool_output" and tool_capture.get("present") is True and tool_capture.get("receipt_sha256"):
            content_origin = "tool_observed"
            claimed_source_status = "verified_tool_receipt"
        else:
            content_origin = "unknown"
            claimed_source_status = "unverified_not_tool_observed"
    elif provenance_rule and source == "unknown":
        content_origin = "unknown"
        claimed_source_status = "unverified_not_tool_observed" if claimed_source else "not_claimed"
    else:
        content_origin = "source_not_challenged"
        claimed_source_status = "not_assessed"

    # A direct human claim is not enough; this fixture contains no verified
    # direct-permission evidence, so no rule grants user_direct authority.
    if actor_type == "unknown":
        authority = "unknown"

    result = {
        "actor_type": actor_type,
        "actor_id": actor_id,
        "source": source,
        "principal_status": principal_status,
        "principal_id": principal_id,
        "authority": authority,
        "content_origin": content_origin,
        "claimed_source_status": claimed_source_status,
        "policy": "evidence_based_carried_rules",
        "rules_applied": sorted(rules),
    }
    return result


def _expected_matches(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())


def _manifest(run_id: str, condition: str, case: Mapping[str, Any], policy: str) -> dict[str, Any]:
    context = load_context(CONTEXT_ID)
    config = {
        "policy": policy,
        "skill_id": "separate-actor-identity-classification-and-authority",
        "case_id": case["test_id"],
        "context_supplied": policy == "carried_context",
    }
    return {
        "run_id": run_id,
        "condition_label": condition,
        "task_brief_sha256": _sha256_json(case),
        "condition_config_sha256": _sha256_json(config),
        "logger_version": LOGGER_VERSION,
        "schema_version": SCHEMA_VERSION,
        "started_at_utc": utc_now(),
        "model": MODEL,
        "environment": ENVIRONMENT,
        "resource_limits": RESOURCE_LIMITS,
        "base_commit": BASE_COMMIT,
        "context_id": CONTEXT_ID,
        "context": context,
    }


def _run_one(
    root: Path,
    case: Mapping[str, Any],
    run_id: str,
    condition: str,
    policy: str,
    skill_bytes: bytes,
    skill_sha256: str,
    skill: Mapping[str, Any],
    carry_context: Mapping[str, Any] | None = None,
    rules: set[str] | None = None,
) -> dict[str, Any]:
    workspace = root / "workspaces" / run_id
    run_dir = root / "runs" / case["test_id"] / run_id
    workspace.mkdir(parents=True, exist_ok=False)
    logger = RunLogger(run_dir, workspace, _manifest(run_id, condition, case, policy))
    try:
        case_ref = logger.capture_artifact("case-input.json", _json_bytes(case), "application/json")
        skill_ref = logger.capture_artifact("portable-skill-snapshot.json", skill_bytes, "application/json")
        input_refs = [case_ref, skill_ref]
        if carry_context is not None:
            carry_ref = logger.capture_artifact("carried-context.json", _json_bytes(carry_context), "application/json")
            input_refs.append(carry_ref)
        logger.emit(
            "preflight_check", "runner", "preflight", "succeeded",
            {
                "check": "declared_test_inputs",
                "test_id": case["test_id"],
                "policy": policy,
                "portable_skill_sha256": skill_sha256,
                "carry_context_supplied": carry_context is not None,
                "carried_rule_ids": sorted(rules or set()),
            },
            input_refs,
        )

        baseline = legacy_decision(case)
        if policy in {"skill_diagnostic", "carried_context"}:
            decision = evidence_based_decision(case, rules or set())
        else:
            decision = baseline

        expected = case["expected"]
        passed = _expected_matches(decision, expected)
        output = {
            "test_id": case["test_id"],
            "run_id": run_id,
            "condition": condition,
            "policy": policy,
            "baseline_decision": baseline if policy == "skill_diagnostic" else None,
            "decision": decision,
            "expected": expected,
            "matched_expected": passed,
        }
        result_ref = logger.capture_artifact("decision-result.json", _json_bytes(output), "application/json")
        logger.emit(
            "requirement_check", "reviewer", "verification",
            "succeeded" if passed else "failed",
            {
                "requirement_id": f"{case['test_id']}-expected-classification",
                "result": "pass" if passed else "fail",
                "expected_sha256": _sha256_json(expected),
                "decision_sha256": _sha256_json(decision),
                "matched_expected": passed,
                "policy": policy,
            },
            [result_ref],
        )
        logger.record_test_result(
            ["deterministic-actor-attribution-evaluator", case["test_id"], policy],
            0 if passed else 1,
            1 if passed else 0,
            0 if passed else 1,
            [result_ref],
        )
        # The run itself completed successfully even when the evaluated policy
        # misclassified the case. Keep execution validity separate from outcome.
        logger.finish("succeeded", "Deterministic policy evaluation completed; matched_expected records the outcome.")
    finally:
        logger.close()
    validation = validate_run(run_dir)
    return {
        "run_id": run_id,
        "condition": condition,
        "policy": policy,
        "decision": decision,
        "baseline_decision": baseline if policy == "skill_diagnostic" else None,
        "expected": expected,
        "matched_expected": passed,
        "run_dir": run_dir.relative_to(root).as_posix(),
        "events_sha256": validation["events_sha256"],
        "events": validation["events"],
        "evidence_refs_verified": validation["evidence_refs_verified"],
        "validation": validation["status"],
        "result_artifact": result_ref,
    }


def _derive_findings(
    case1: Mapping[str, Any],
    result1: Mapping[str, Any],
    case2: Mapping[str, Any],
    result2: Mapping[str, Any],
) -> list[dict[str, Any]]:
    a = result1["decision"]
    c1 = case1["input"]
    grant1 = c1.get("delegation_evidence") or {}
    if not (
        a.get("actor_id") == c1["host_identity"]["actor_id"]
        and a.get("principal_status") == "unverified_claim"
        and a.get("authority") == "unknown"
        and grant1.get("verified") is False
    ):
        raise RuntimeError(
            "T1 did not produce the expected performer/principal/authority distinction: "
            + json.dumps({"decision": a, "host_identity": c1["host_identity"],
                          "claims": c1.get("self_asserted_claims"), "grant": grant1}, sort_keys=True)
        )

    b = result2["decision"]
    c2 = case2["input"]
    if not (
        b.get("source") == c2["trusted_transport"]["source"]
        and b.get("claimed_source_status") == "unverified_not_tool_observed"
        and c2["tool_capture"].get("present") is False
    ):
        raise RuntimeError("T2 did not produce the expected transport/provenance distinction")

    return [
        {
            "rule_id": RULE_PRINCIPAL,
            "conclusion": case1["finding_conclusion"],
            "when_to_apply": case1["finding_when"],
            "source_test_id": case1["test_id"],
            "source_run_id": result1["run_id"],
            "source_events_sha256": result1["events_sha256"],
            "source_result_artifact": result1["result_artifact"],
            "portable_skill_method_steps": [3, 5, 6, 7],
        },
        {
            "rule_id": RULE_PROVENANCE,
            "conclusion": case2["finding_conclusion"],
            "when_to_apply": case2["finding_when"],
            "source_test_id": case2["test_id"],
            "source_run_id": result2["run_id"],
            "source_events_sha256": result2["events_sha256"],
            "source_result_artifact": result2["result_artifact"],
            "portable_skill_method_steps": [2, 4, 7],
        },
    ]


def run_batch(output: str | Path) -> dict[str, Any]:
    root = Path(output).resolve()
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"output must be new or empty: {root}")
    root.mkdir(parents=True, exist_ok=True)
    (root / "runs").mkdir()
    (root / "workspaces").mkdir()

    casebook, skill, pin, skill_sha256 = _load_inputs()
    cases = {item["test_id"]: item for item in casebook["cases"]}
    if set(cases) != {"T1", "T2", "T3", "T4"}:
        raise ValueError("the transfer batch must contain exactly T1, T2, T3, and T4")
    skill_bytes = SKILL_PATH.read_bytes()
    skill_rules = _rules_from_skill(skill)

    # Phase 1: early diagnostic tests apply the pinned portable skill.
    t1 = _run_one(root, cases["T1"], "T1-skill", "REHEARSAL-A",
                  "skill_diagnostic", skill_bytes, skill_sha256, skill, rules=skill_rules)
    t2 = _run_one(root, cases["T2"], "T2-skill", "REHEARSAL-B",
                  "skill_diagnostic", skill_bytes, skill_sha256, skill, rules=skill_rules)

    findings = _derive_findings(cases["T1"], t1, cases["T2"], t2)
    carry_context = {
        "format_version": "1.0",
        "record_type": "portable_test_learning_context",
        "context_id": "actor-attribution-lessons-derived-from-T1-T2-v1",
        "created_after_tests": ["T1", "T2"],
        "source_skill_id": skill["skill_id"],
        "source_skill_sha256": skill_sha256,
        "rules": findings,
        "limitations": [
            "Derived from two synthetic cases in this batch.",
            "This is deterministic rule transfer, not model learning or proof of human/agent generalisation.",
            "The context only supports the synthetic fields and evidence model defined by these cases."
        ]
    }
    carry_bytes = _json_bytes(carry_context)
    carry_path = root / "carried-context" / "actor-attribution-lessons.json"
    carry_path.parent.mkdir(parents=True)
    carry_path.write_bytes(carry_bytes)
    carry_sha256 = sha256_bytes(carry_bytes)
    carried_rules = {item["rule_id"] for item in findings}

    # Phase 2: each new case is run twice from the same declared fixture baseline.
    later: dict[str, dict[str, Any]] = {}
    for test_id in ("T3", "T4"):
        case = cases[test_id]
        baseline = _run_one(
            root, case, f"{test_id}-no-context", "A", "no_context",
            skill_bytes, skill_sha256, skill,
        )
        context = _run_one(
            root, case, f"{test_id}-carried-context", "B", "carried_context",
            skill_bytes, skill_sha256, skill, carry_context=carry_context, rules=carried_rules,
        )
        pair = validate_pair(
            root / baseline["run_dir"], root / context["run_dir"],
            {"run_started", "preflight_check", "requirement_check", "test_result", "run_finished"},
        )
        if pair["status"] != "PASS":
            raise RuntimeError(f"{test_id} comparison pair failed Q-Batch validation")
        if baseline["expected"] != context["expected"]:
            raise RuntimeError(f"{test_id} expected result changed between conditions")
        later[test_id] = {
            "baseline_without_context": baseline,
            "with_carried_context": context,
            "pair_validation": pair,
            "transfer_rule_ids": [rule for rule in case.get("transfer_rule_ids", [case["finding_rule_id"]])
                                  if rule in carried_rules],
        }

    t3_ok = (
        not later["T3"]["baseline_without_context"]["matched_expected"]
        and later["T3"]["with_carried_context"]["matched_expected"]
        and later["T3"]["with_carried_context"]["decision"]["authority"] == "delegated_authority_verified"
        and later["T3"]["with_carried_context"]["decision"]["actor_id"] == "service:maintenance"
    )
    t4_ok = (
        not later["T4"]["baseline_without_context"]["matched_expected"]
        and later["T4"]["with_carried_context"]["matched_expected"]
        and later["T4"]["with_carried_context"]["decision"]["actor_type"] == "unknown"
        and later["T4"]["with_carried_context"]["decision"]["source"] == "unknown"
        and later["T4"]["with_carried_context"]["decision"]["authority"] == "unknown"
    )
    all_valid = all(
        result["validation"] == "succeeded"
        for result in (t1, t2)
    ) and all(
        item[key]["validation"] == "succeeded"
        for item in later.values()
        for key in ("baseline_without_context", "with_carried_context")
    )
    context_provenance_complete = all(
        rule.get("source_run_id")
        and rule.get("source_events_sha256")
        and rule.get("source_result_artifact", {}).get("sha256")
        for rule in findings
    )
    overall = all((t1["matched_expected"], t2["matched_expected"], t3_ok, t4_ok,
                   all_valid, context_provenance_complete,
                   all(item["pair_validation"]["status"] == "PASS" for item in later.values())))
    report = {
        "status": "PASS" if overall else "FAIL",
        "classification": casebook["classification"],
        "purpose": "Test whether T1/T2 conclusions can be carried as a file and improve later T3/T4 classifications.",
        "skill_source": {
            "repository": pin["source_repository"],
            "commit": pin["source_commit"],
            "path": pin["source_path"],
            "source_blob_sha1_verified": pin["source_blob_sha1"],
            "snapshot_sha256": skill_sha256
        },
        "execution_order": ["T1-skill", "T2-skill", "derive-carried-context", "T3-no-context", "T3-carried-context",
                            "T4-no-context", "T4-carried-context"],
        "early_diagnostics": {"T1": t1, "T2": t2},
        "carried_context": {
            "path": carry_path.relative_to(root).as_posix(),
            "sha256": carry_sha256,
            "created_from": ["T1", "T2"],
            "findings": findings
        },
        "later_transfer_tests": later,
        "analysis": {
            "T1_passed": t1["matched_expected"],
            "T2_passed": t2["matched_expected"],
            "T3_improved_by_T1_context": t3_ok,
            "T4_improved_by_T1_T2_context": t4_ok,
            "all_six_run_logs_valid": all_valid,
            "both_later_pairs_validated": all(item["pair_validation"]["status"] == "PASS" for item in later.values()),
            "carried_context_has_source_receipts": context_provenance_complete,
            "model_calls": 0,
            "external_services": 0,
            "runs": 6
        },
        "interpretation": [
            "T1's finding about performer, claimed principal and verified delegation is carried into T3, where a genuinely valid scoped grant must be recognised rather than rejected by actor type.",
            "T2's finding about trusted transport and tool receipts is carried into T4, where self-described human/tool labels must not override absent identity and transport evidence.",
            "Each later test is executed once without the carried context and once with it; both paired runs start from the same declared test baseline.",
            "The experiment tests deterministic rule transfer and Q-Batch evidence handling. It does not test a language model's ability to read or learn from the portable file."
        ],
        "limitations": [
            "All cases and evidence are synthetic.",
            "The policy evaluator is deterministic and explicitly implements the reviewed rules; this is not a blind test of model reasoning.",
            "The result is limited to these four cases and does not establish production authentication, permission, or event-source correctness.",
            "The carried context is derived only from T1/T2 within this batch; it is not a universal skill or a replacement for human review."
        ]
    }
    (root / "batch-report.json").write_bytes(_json_bytes(report))
    if not overall:
        raise RuntimeError("actor-attribution transfer batch failed; inspect batch-report.json")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New or empty directory for the six-run evidence batch")
    args = parser.parse_args()
    report = run_batch(args.output)
    print(json.dumps({
        "status": report["status"],
        "classification": report["classification"],
        "analysis": report["analysis"],
        "report": str(Path(args.output).resolve() / "batch-report.json"),
        "carried_context": str(Path(args.output).resolve() / report["carried_context"]["path"])
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Dependency-free structural and reconstruction checks for Q-Batch AEL evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "qbatch-ael-runtime-evidence/0.1"
TOP_REQUIRED = {"schema_version", "batch_id", "purpose", "specification_ref", "condition", "status", "events", "outputs", "limitations", "ael_runtime"}
AEL_REQUIRED = {"runtime_version", "runtime_source_sha", "ledger_ref", "ledger_high_watermark", "audit_sidecar_ref", "model_input_ref", "response_ref", "model_call", "boundary_checks", "failure_point", "recovery"}
MODEL_CALL_REQUIRED = {"adapter", "model", "endpoint_class", "inference_mode"}
VALID_STATUSES = {"planned", "incomplete", "passed", "failed", "blocked"}
VALID_INFERENCE_MODES = {"real", "mocked", "not_attempted"}

def validate_record(record: Any, require_reconstructable: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    missing = sorted(TOP_REQUIRED - record.keys())
    if missing:
        errors.append("missing top-level fields: " + ", ".join(missing))
    if record.get("schema_version") != SCHEMA:
        errors.append(f"schema_version must be {SCHEMA!r}")
    for field in ("batch_id", "purpose", "specification_ref", "condition"):
        if field in record and (not isinstance(record[field], str) or not record[field].strip()):
            errors.append(f"{field} must be a non-empty string")
    if record.get("status") not in VALID_STATUSES:
        errors.append("status must be one of: " + ", ".join(sorted(VALID_STATUSES)))
    for field in ("events", "outputs", "limitations"):
        if field in record and not isinstance(record[field], list):
            errors.append(f"{field} must be an array")
    ael = record.get("ael_runtime")
    if not isinstance(ael, dict):
        errors.append("ael_runtime must be an object")
        ael = {}
    else:
        missing_ael = sorted(AEL_REQUIRED - ael.keys())
        if missing_ael:
            errors.append("missing ael_runtime fields: " + ", ".join(missing_ael))
    model_call = ael.get("model_call")
    if not isinstance(model_call, dict):
        errors.append("ael_runtime.model_call must be an object")
        model_call = {}
    else:
        missing_call = sorted(MODEL_CALL_REQUIRED - model_call.keys())
        if missing_call:
            errors.append("missing model_call fields: " + ", ".join(missing_call))
        if model_call.get("inference_mode") not in VALID_INFERENCE_MODES:
            errors.append("inference_mode must be real, mocked, or not_attempted")
    if not isinstance(ael.get("boundary_checks", []), list):
        errors.append("ael_runtime.boundary_checks must be an array")
    recovery = ael.get("recovery")
    if not isinstance(recovery, dict) or not isinstance(recovery.get("attempted"), bool):
        errors.append("ael_runtime.recovery.attempted must be a boolean")
    if record.get("status") == "failed" and not ael.get("failure_point"):
        errors.append("failed records must name ael_runtime.failure_point")
    if model_call.get("inference_mode") == "not_attempted" and ael.get("response_ref") is not None:
        errors.append("response_ref must be null when inference_mode is not_attempted")

    if require_reconstructable:
        if not record.get("started_at"):
            errors.append("reconstruction: started_at is missing")
        if not record.get("ended_at"):
            errors.append("reconstruction: ended_at is missing")
        if not record.get("executor") or not isinstance(record.get("environment"), dict):
            errors.append("reconstruction: executor and environment details are required")
        if not record.get("procedure"):
            errors.append("reconstruction: procedure is missing")
        if not record.get("events"):
            errors.append("reconstruction: no event records preserved")
        if not record.get("provenance") or not isinstance(record.get("provenance"), dict):
            errors.append("reconstruction: collection provenance is missing")
        if not ael.get("runtime_source_sha"):
            errors.append("reconstruction: immutable runtime source revision is missing")
        if not model_call.get("inference_mode"):
            errors.append("reconstruction: model-call mode is unknown")
        if record.get("status") == "failed" and not ael.get("failure_point"):
            errors.append("reconstruction: failure point is unknown")
        evidence_refs = []
        for output in record.get("outputs", []) if isinstance(record.get("outputs"), list) else []:
            if isinstance(output, dict) and output.get("availability") in (None, "preserved") and output.get("path") and output.get("sha256"):
                evidence_refs.append(output)
        for field in ("ledger_ref", "audit_sidecar_ref", "model_input_ref", "response_ref"):
            ref = ael.get(field)
            if ref is not None and not (isinstance(ref, dict) and ref.get("path") and ref.get("sha256")):
                errors.append(f"reconstruction: {field} must include path and sha256 when supplied")
        if not evidence_refs and not any(isinstance(ael.get(f), dict) and ael[f].get("path") and ael[f].get("sha256") for f in ("ledger_ref", "audit_sidecar_ref", "model_input_ref", "response_ref")):
            errors.append("reconstruction: no preserved, hashed output or AEL artifact is referenced")
        limitations = record.get("limitations", [])
        if any("synthetic" in str(x).lower() or "illustrative" in str(x).lower() for x in limitations):
            errors.append("reconstruction: record is explicitly synthetic/illustrative, not observed evidence")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="JSON evidence record")
    parser.add_argument("--reconstruct", action="store_true", help="also require sufficient preserved evidence for reconstruction")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: cannot read JSON: {exc}")
        return 2
    errors = validate_record(record, require_reconstructable=args.reconstruct)
    if errors:
        print("INVALID" if not args.reconstruct else "NOT RECONSTRUCTABLE")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID AND RECONSTRUCTABLE" if args.reconstruct else "STRUCTURALLY VALID")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_ael_evidence import validate_record

def fixture():
    return {
        "schema_version": "qbatch-ael-runtime-evidence/0.1",
        "extends": ["basic-evidence-log/0.1"],
        "batch_id": "unit-test-001", "purpose": "validator unit test",
        "specification_ref": "formats/AEL_RUNTIME_EVIDENCE.md", "condition": "test",
        "started_at": "2026-10-27T12:00:00Z", "ended_at": "2026-10-27T12:00:01Z",
        "executor": {"name": "unit-test", "version": "1"},
        "environment": {"os": "test-os", "reset": "clean", "persistence": "known"},
        "inputs": [], "resources": [], "procedure": ["Run a validator test"],
        "status": "failed",
        "events": [{"event_id": "e1", "sequence": 1, "timestamp": "2026-10-27T12:00:00Z", "type": "error"}],
        "outputs": [{"path": "outputs/stderr.txt", "sha256": "a" * 64, "availability": "preserved"}],
        "deviations": [], "limitations": [],
        "provenance": {"collector": "unit-test", "collected_at": "2026-10-27T12:00:01Z"},
        "interpretation": None,
        "ael_runtime": {
            "runtime_version": "test", "runtime_source_sha": "deadbeef", "ledger_ref": None,
            "ledger_high_watermark": None, "audit_sidecar_ref": None, "model_input_ref": None,
            "response_ref": None,
            "model_call": {"adapter": "test", "model": "none", "endpoint_class": "loopback", "inference_mode": "not_attempted"},
            "boundary_checks": [], "failure_point": "preflight",
            "recovery": {"attempted": False, "prior_attempt_batch_id": None, "notes": None}
        }
    }

class AelEvidenceValidatorTests(unittest.TestCase):
    def test_incomplete_template_is_structural_but_not_reconstructable(self):
        record = fixture()
        record.update(status="incomplete", started_at=None, ended_at=None, procedure=[], events=[], outputs=[])
        record["executor"] = {"name": "to-be-recorded", "version": None}
        record["provenance"] = {"collector": None, "collected_at": None}
        record["ael_runtime"]["runtime_source_sha"] = None
        self.assertEqual(validate_record(record), [])
        self.assertTrue(any("started_at" in e for e in validate_record(record, True)))

    def test_rejects_missing_required_field(self):
        record = fixture(); del record["batch_id"]
        self.assertTrue(any("batch_id" in e for e in validate_record(record)))

    def test_rejects_unknown_inference_mode(self):
        record = fixture(); record["ael_runtime"]["model_call"]["inference_mode"] = "probably-real"
        self.assertTrue(any("inference_mode" in e for e in validate_record(record)))

    def test_failed_run_requires_failure_point(self):
        record = fixture(); record["ael_runtime"]["failure_point"] = None
        self.assertTrue(any("failure_point" in e for e in validate_record(record)))

    def test_not_attempted_cannot_claim_response(self):
        record = fixture(); record["ael_runtime"]["response_ref"] = {"path": "response.json", "sha256": "abc"}
        self.assertTrue(any("response_ref must be null" in e for e in validate_record(record)))

    def test_synthetic_record_fails_observed_reconstruction(self):
        record = fixture(); record["limitations"] = ["Synthetic fixture only; illustrative, not observed evidence."]
        errors = validate_record(record, True)
        self.assertTrue(any("synthetic/illustrative" in e for e in errors))

    def test_reconstructable_observed_failure_passes(self):
        self.assertEqual(validate_record(fixture(), True), [])

if __name__ == "__main__":
    unittest.main(verbosity=2)

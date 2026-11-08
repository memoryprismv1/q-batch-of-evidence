"""Regression tests for the actor-attribution cross-test transfer batch."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.actor_attribution_transfer.runner import run_batch
from experiments.ct_ab.validate_log import validate_run


class ActorAttributionTransferBatchTests(unittest.TestCase):
    def test_t1_t2_conclusions_transfer_to_t3_t4(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "actor-transfer-batch"
            report = run_batch(output)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                report["classification"],
                "SYNTHETIC_DETERMINISTIC_KNOWLEDGE_TRANSFER_NOT_MODEL_LEARNING",
            )
            self.assertEqual(report["analysis"]["runs"], 6)
            self.assertEqual(report["analysis"]["model_calls"], 0)
            self.assertEqual(report["analysis"]["external_services"], 0)
            self.assertTrue(report["analysis"]["T1_passed"])
            self.assertTrue(report["analysis"]["T2_passed"])
            self.assertTrue(report["analysis"]["T3_improved_by_T1_context"])
            self.assertTrue(report["analysis"]["T4_improved_by_T1_T2_context"])
            self.assertTrue(report["analysis"]["both_later_pairs_validated"])
            self.assertTrue(report["analysis"]["carried_context_has_source_receipts"])

            # T1: the host-verified agent remains the actor; a self-asserted
            # different actor/principal and claimed delegation do not grant power.
            t1 = report["early_diagnostics"]["T1"]
            self.assertEqual(t1["decision"]["actor_id"], "agent:planner")
            self.assertEqual(t1["decision"]["principal_status"], "unverified_claim")
            self.assertEqual(t1["decision"]["authority"], "unknown")
            self.assertEqual(t1["baseline_decision"]["actor_id"], "agent:lookalike")
            self.assertEqual(t1["baseline_decision"]["authority"], "delegated_by_claim")

            # T2: quoted tool-like text does not create a tool-origin event.
            t2 = report["early_diagnostics"]["T2"]
            self.assertEqual(t2["decision"]["source"], "human_chat")
            self.assertEqual(t2["decision"]["content_origin"], "human_submitted_statement")
            self.assertEqual(t2["decision"]["claimed_source_status"], "unverified_not_tool_observed")
            self.assertEqual(t2["baseline_decision"]["source"], "tool_output")

            carry_path = output / report["carried_context"]["path"]
            carry = json.loads(carry_path.read_text(encoding="utf-8"))
            self.assertEqual(carry["created_after_tests"], ["T1", "T2"])
            self.assertEqual(
                {finding["rule_id"] for finding in carry["rules"]},
                {
                    "separate_claimed_principal_from_verified_authority",
                    "derive_provenance_from_trusted_transport",
                },
            )
            self.assertTrue(all(f["source_result_artifact"]["sha256"] for f in carry["rules"]))
            self.assertTrue(all(f["source_events_sha256"] for f in carry["rules"]))

            # T3 is a positive delegation case. The carried T1 conclusion must
            # not turn "agent/service" into an automatic denial: a valid
            # authenticated grant with a matching action scope is recognised.
            t3 = report["later_transfer_tests"]["T3"]
            self.assertFalse(t3["baseline_without_context"]["matched_expected"])
            self.assertEqual(t3["baseline_without_context"]["decision"]["authority"], "none")
            self.assertTrue(t3["with_carried_context"]["matched_expected"])
            self.assertEqual(
                t3["with_carried_context"]["decision"]["authority"],
                "delegated_authority_verified",
            )
            self.assertEqual(
                t3["transfer_rule_ids"],
                ["separate_claimed_principal_from_verified_authority"],
            )

            # T4 contains human/tool claims but no trusted identity or transport.
            # Both earlier lessons help preserve uncertainty instead of
            # manufacturing a human actor, tool source or direct-user authority.
            t4 = report["later_transfer_tests"]["T4"]
            self.assertFalse(t4["baseline_without_context"]["matched_expected"])
            self.assertEqual(t4["baseline_without_context"]["decision"]["actor_type"], "human")
            self.assertEqual(t4["baseline_without_context"]["decision"]["source"], "tool_output")
            self.assertEqual(t4["baseline_without_context"]["decision"]["authority"], "user_direct")
            self.assertTrue(t4["with_carried_context"]["matched_expected"])
            self.assertEqual(t4["with_carried_context"]["decision"]["actor_type"], "unknown")
            self.assertEqual(t4["with_carried_context"]["decision"]["actor_id"], None)
            self.assertEqual(t4["with_carried_context"]["decision"]["source"], "unknown")
            self.assertEqual(t4["with_carried_context"]["decision"]["authority"], "unknown")
            self.assertEqual(
                t4["transfer_rule_ids"],
                [
                    "separate_claimed_principal_from_verified_authority",
                    "derive_provenance_from_trusted_transport",
                ],
            )
            self.assertEqual(
                set(t4["with_carried_context"]["decision"]["rules_applied"]),
                {
                    "separate_claimed_principal_from_verified_authority",
                    "derive_provenance_from_trusted_transport",
                },
            )

            # All six execution logs are separately validated and retained.
            run_dirs = sorted((output / "runs").glob("*/*"))
            self.assertEqual(len(run_dirs), 6)
            for run_dir in run_dirs:
                result = validate_run(run_dir)
                self.assertEqual(result["status"], "succeeded")
                self.assertGreater(result["evidence_refs_verified"], 0)

            saved_report = json.loads((output / "batch-report.json").read_text(encoding="utf-8"))
            self.assertEqual(saved_report["status"], "PASS")
            self.assertEqual(saved_report["carried_context"]["sha256"], report["carried_context"]["sha256"])

    def test_nonempty_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "existing-batch"
            output.mkdir()
            keep = output / "keep.txt"
            keep.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run_batch(output)
            self.assertEqual(keep.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()

"""Harness tests only: the fake client is not evidence of model learning."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.ai_generated_team_learning.runner import (
    build_classification_messages,
    build_learning_messages,
    run_experiment,
    validate_candidate_anonymisation,
    validate_learning_context,
)
from experiments.ct_ab.validate_log import validate_run

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def _json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


class FakeModelClient:
    provider = "test-double"

    def __init__(self):
        self.calls = []
        self.expected = json.loads((PACKAGE / "scoring" / "expected.json").read_text(encoding="utf-8"))

    def chat(self, request_body):
        self.calls.append(request_body)
        user = json.loads(request_body["messages"][1]["content"])
        if user["task"] == "extract_supplemental_portable_team_learning":
            output = {
                "status": "additional_context",
                "title": "Synthetic test-example addendum",
                "summary": "A test-only fake answer used to exercise the runner.",
                "lessons": [{
                    "lesson_id": "fake-example-boundary",
                    "statement": "Example lesson produced by the fake client.",
                    "apply_when": ["A test asserts a structured transfer run."],
                    "guidance": ["Keep the original evidence attached."],
                    "do_not_infer": ["Do not treat a fake model as a real model result."],
                    "boundary_conditions": ["This object is only a test fixture."],
                    "supporting_examples": ["T1", "T2"],
                    "confidence": "low"
                }],
                "unresolved_questions": ["No model was invoked in this unit test."],
                "limitations": ["Fake output is not an AI-generated finding."]
            }
        else:
            test_id = user["case"]["test_id"]
            output = dict(self.expected[test_id])
            if user["supplemental_team_learning"] is None:
                # Deliberate fixture errors in the base-only arm. These test
                # that the scorer detects both gains and negative boundaries.
                if test_id == "T3":
                    output["authority"] = "unknown"
                elif test_id == "T4":
                    output.update({
                        "actor_type": "human", "actor_id": "human:release_manager",
                        "source": "tool_output", "content_origin": "tool_observed",
                        "authority": "user_direct"
                    })
                elif test_id == "T5":
                    output["content_origin"] = "human_submitted_statement"
                    output["claimed_source_status"] = "unverified_not_tool_observed"
                elif test_id == "T6":
                    output["authority"] = "delegated_authority_verified"
        required = set(request_body["format"]["required"])
        if set(output) != required:
            raise AssertionError("fake output does not match requested schema")
        return {
            "model": "fake-model",
            "done": True,
            "message": {"role": "assistant", "content": _json_text(output)},
            "prompt_eval_count": 10,
            "eval_count": 20,
            "total_duration": 1000
        }


class AIGeneratedTeamLearningTests(unittest.TestCase):
    def setUp(self):
        self.learning = json.loads((PACKAGE / "inputs" / "learning_examples.json").read_text(encoding="utf-8"))
        self.transfer = json.loads((PACKAGE / "inputs" / "transfer_cases.json").read_text(encoding="utf-8"))
        self.expected = json.loads((PACKAGE / "scoring" / "expected.json").read_text(encoding="utf-8"))
        base_skill_path = ROOT / "experiments" / "actor_attribution_transfer" / "inputs" / "actor-attribution-portable-skill.json"
        self.skill = json.loads(base_skill_path.read_text(encoding="utf-8"))

    def test_learning_prompt_contains_only_t1_t2_and_no_gold_answers(self):
        messages = build_learning_messages(self.skill, self.learning)
        combined = "\n".join(item["content"] for item in messages)
        self.assertIn('"example_id": "T1"', combined)
        self.assertIn('"example_id": "T2"', combined)
        for test_id in ("T3", "T4", "T5", "T6"):
            self.assertNotIn(test_id, combined)
        self.assertNotIn('"expected"', combined.lower())
        self.assertNotIn("not_authorized_for_requested_action", combined)
        self.assertNotIn("verified_tool_receipt", combined)

    def test_transfer_prompt_does_not_include_case_gold_answer(self):
        for case in self.transfer["cases"]:
            messages = build_classification_messages(self.skill, case, None)
            combined = "\n".join(item["content"] for item in messages)
            self.assertNotIn('"expected"', combined)
            self.assertNotIn("not_authorized_for_requested_action", combined)
            self.assertIn(case["test_id"], combined)

    def test_candidate_must_not_copy_source_identifiers_or_raw_content(self):
        pin = json.loads((ROOT / "experiments" / "actor_attribution_transfer" / "inputs" / "skill-source-pin.json").read_text(encoding="utf-8"))
        candidate = {
            "status": "additional_context", "title": "General rule", "summary": "Generalised.",
            "lessons": [{
                "lesson_id": "generic", "statement": "Separate actor and claimed principal.",
                "apply_when": ["A message claims representation."], "guidance": ["Check trusted evidence."],
                "do_not_infer": ["Do not infer authority from a claim."],
                "boundary_conditions": ["Only where the receiving system exposes such evidence."],
                "supporting_examples": ["T1"], "confidence": "medium"
            }], "unresolved_questions": [], "limitations": ["Two synthetic examples only."]
        }
        validate_candidate_anonymisation(candidate, self.learning, pin)
        leaked = json.loads(json.dumps(candidate))
        leaked["lessons"][0]["statement"] = "Do not trust agent:planner."
        with self.assertRaises(ValueError):
            validate_candidate_anonymisation(leaked, self.learning, pin)

    def test_no_additional_context_is_a_valid_learning_outcome(self):
        validate_learning_context({
            "status": "no_additional_context", "title": "No additional context",
            "summary": "The examples add no supported information beyond the base skill.",
            "lessons": [], "unresolved_questions": [], "limitations": ["Synthetic examples only."]
        })

    def test_fake_harness_produces_nine_stateless_runs_and_pairs(self):
        client = FakeModelClient()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "ai-learning-batch"
            report = run_experiment(
                output, "fake-model", client,
                model_info={"provider": "test-double", "digest": "not-a-real-model"},
                ollama_version="fake", seed=23
            )
            self.assertEqual(report["status"], "COMPLETE")
            self.assertEqual(report["classification"], "HARNESS_TEST_NOT_MODEL_EVIDENCE")
            self.assertEqual(report["model_calls"], 9)
            self.assertEqual(len(client.calls), 9)
            self.assertEqual(set(report["transfer_pairs"]), {"T3", "T4", "T5", "T6"})
            self.assertTrue(all(x["pair_validation"]["status"] == "PASS" for x in report["transfer_pairs"].values()))

            key_path = Path(report["controller_key_path"])
            key = json.loads(key_path.read_text(encoding="utf-8"))
            self.assertEqual(set(key["cases"]), {"T3", "T4", "T5", "T6"})
            for test_id, pair in report["transfer_pairs"].items():
                self.assertEqual(set(key["cases"][test_id].values()), {"base_skill_only", "base_skill_plus_generated_context"})
                for label in ("A", "B"):
                    run = pair[label]
                    self.assertEqual(run["run_validation"], "succeeded")
                    self.assertIsNotNone(run["decision"])
                    self.assertEqual(
                        run["score"]["exact_match"],
                        key["cases"][test_id][label] == "base_skill_plus_generated_context"
                    )

            run_dirs = sorted((output / "runs").glob("*/*"))
            self.assertEqual(len(run_dirs), 9)
            for run_dir in run_dirs:
                self.assertEqual(validate_run(run_dir)["status"], "succeeded")

            treatment_label = next(
                label for label in ("A", "B")
                if key["cases"]["T3"][label] == "base_skill_plus_generated_context"
            )
            treatment_prompt_path = next(
                (output / "runs" / "T3" / f"T3-{treatment_label}" / "artifacts").glob("*model-request.json")
            )
            treatment_prompt = json.loads(treatment_prompt_path.read_text(encoding="utf-8"))
            treatment_payload = json.loads(treatment_prompt["messages"][1]["content"])
            self.assertIn("provenance", treatment_payload["supplemental_team_learning"])
            self.assertEqual(
                treatment_payload["supplemental_team_learning"]["provenance"]["source_evidence"][0]["example_id"],
                "T1"
            )

            # The saved extraction request still contains only T1/T2.
            learn_request = next(
                (output / "runs" / "LEARN" / "LEARN-T1-T2" / "artifacts").glob("*model-request.json")
            )
            prompt = json.loads(learn_request.read_text(encoding="utf-8"))
            prompt_text = json.dumps(prompt, ensure_ascii=False)
            for test_id in ("T3", "T4", "T5", "T6"):
                self.assertNotIn(test_id, prompt_text)

    def test_existing_controller_key_stops_before_any_model_call(self):
        client = FakeModelClient()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "ai-learning-batch"
            key_dir = output.parent / f".{output.name}-controller-private"
            key_dir.mkdir()
            (key_dir / "condition-key.json").write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run_experiment(output, "fake-model", client, model_info={"provider": "test-double"})
            self.assertEqual(client.calls, [])

    def test_nonempty_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "existing"
            output.mkdir()
            marker = output / "keep.txt"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run_experiment(output, "fake-model", FakeModelClient(), model_info={"provider": "test-double"})
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()

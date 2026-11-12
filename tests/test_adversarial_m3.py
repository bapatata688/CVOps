#!/usr/bin/env python3
"""test_adversarial_m3.py - Adversarial Stress & Integrity Harness for Milestone 3

Rigorously verifies:
1. JSON schema and integrity of questions_db.json and evaluation_rubrics.json.
2. Cross-check consistency between INTERVIEW_DEFENSE_MANUAL.md and resources/evidence_matrix.json.
3. Git layout and SHA256 byte-parity between master_cv and coe skill directories.
4. Adversarial fuzzing and stress tests of scripts/drill_runner.py with bizarre, unicode,
   massive, empty, and malicious inputs.

Compliance:
- Zero Pytest / Zero Matplotlib (AGENTS.md Rule 5 compliant).
- Python standard library unittest only.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR_MASTER = REPO_ROOT / ".agents" / "skills" / "cv-interview-defense"
COE_ROOT = Path("c:/Users/Usuario/Projects/coe")
SKILL_DIR_COE = COE_ROOT / ".agents" / "skills" / "cv-interview-defense"

QUESTIONS_DB_PATH = SKILL_DIR_MASTER / "resources" / "questions_db.json"
RUBRICS_PATH = SKILL_DIR_MASTER / "resources" / "evaluation_rubrics.json"
EVIDENCE_MATRIX_PATH = SKILL_DIR_MASTER / "resources" / "evidence_matrix.json"
DRILL_RUNNER_PATH = SKILL_DIR_MASTER / "scripts" / "drill_runner.py"
MANUAL_PATH = REPO_ROOT / "docs" / "INTERVIEW_DEFENSE_MANUAL.md"


class TestQuestionDatabaseIntegrity(unittest.TestCase):
    """Adversarially tests questions_db.json schema, referential integrity, and contents."""

    def setUp(self):
        self.assertTrue(QUESTIONS_DB_PATH.is_file(), f"Missing {QUESTIONS_DB_PATH}")
        self.assertTrue(RUBRICS_PATH.is_file(), f"Missing {RUBRICS_PATH}")
        with open(QUESTIONS_DB_PATH, "r", encoding="utf-8") as f:
            self.q_data = json.load(f)
        with open(RUBRICS_PATH, "r", encoding="utf-8") as f:
            self.r_data = json.load(f)

    def test_qdb_schema_and_metadata(self):
        """Validates JSON structure and mandatory metadata keys."""
        self.assertIn("$schema", self.q_data)
        self.assertIn("version", self.q_data)
        self.assertEqual(self.q_data.get("version"), "1.0.0")
        self.assertIn("questions", self.q_data)
        self.assertIsInstance(self.q_data["questions"], list)
        self.assertGreaterEqual(len(self.q_data["questions"]), 10)

    def test_qdb_question_fields_and_uniqueness(self):
        """Validates that each question has all required fields and unique IDs."""
        seen_ids = set()
        required_fields = [
            "question_id", "persona", "project", "title",
            "question_text", "context", "suggested_approach",
            "expected_anchors", "prohibited_terms", "rubric_ref"
        ]

        allowed_personas = {
            "technical", "tech_lead", "ml_researcher",
            "recruiter", "behavioral", "executive", "auditor"
        }
        allowed_projects = {"ontotab", "gbm", "ferrostats", "sql_arena", "sql-arena"}

        rubric_ids = {r["rubric_id"] for r in self.r_data.get("rubrics", [])}

        for idx, q in enumerate(self.q_data["questions"]):
            for field in required_fields:
                self.assertIn(
                    field, q,
                    f"Question at index {idx} (ID: {q.get('question_id', 'UNKNOWN')}) missing '{field}'"
                )

            qid = q["question_id"]
            self.assertNotIn(qid, seen_ids, f"Duplicate question_id: '{qid}'")
            seen_ids.add(qid)

            # Validate persona and project
            persona = q["persona"].lower().strip()
            self.assertIn(persona, allowed_personas, f"Invalid persona '{persona}' in {qid}")

            project = q["project"].lower().strip()
            self.assertIn(project, allowed_projects, f"Invalid project '{project}' in {qid}")

            # Validate rubric reference exists in evaluation_rubrics.json
            self.assertIn(
                q["rubric_ref"], rubric_ids,
                f"Question {qid} references unknown rubric '{q['rubric_ref']}'"
            )

            # Validate anchors and prohibited terms
            self.assertIsInstance(q["expected_anchors"], list)
            self.assertGreaterEqual(len(q["expected_anchors"]), 2, f"Insufficient anchors in {qid}")
            self.assertIsInstance(q["prohibited_terms"], list)
            self.assertGreaterEqual(len(q["prohibited_terms"]), 2, f"Insufficient prohibited terms in {qid}")

    def test_qdb_covers_all_personas_and_projects(self):
        """Verifies full coverage across core personas and all 4 projects."""
        personas_present = {q["persona"] for q in self.q_data["questions"]}
        projects_present = {q["project"] for q in self.q_data["questions"]}

        # All 4 core projects must be present
        self.assertIn("ontotab", projects_present)
        self.assertIn("gbm", projects_present)
        self.assertIn("ferrostats", projects_present)
        self.assertIn("sql_arena", projects_present)

        # Core personas must be present
        self.assertTrue({"technical", "recruiter", "auditor", "behavioral"}.issubset(personas_present))


class TestEvaluationRubricsIntegrity(unittest.TestCase):
    """Adversarially tests evaluation_rubrics.json schema, score bounds, and penalty rules."""

    def setUp(self):
        with open(RUBRICS_PATH, "r", encoding="utf-8") as f:
            self.r_data = json.load(f)

    def test_rubrics_structure_and_score_bounds(self):
        """Validates score ranges, unique IDs, and criteria keys."""
        rubrics = self.r_data.get("rubrics", [])
        self.assertGreaterEqual(len(rubrics), 4)

        seen_rubric_ids = set()
        for r in rubrics:
            self.assertIn("rubric_id", r)
            self.assertNotIn(r["rubric_id"], seen_rubric_ids)
            seen_rubric_ids.add(r["rubric_id"])

            self.assertEqual(r.get("min_score"), 1)
            self.assertEqual(r.get("max_score"), 5)

            criteria = r.get("criteria", {})
            self.assertIn("star_structure", criteria)
            self.assertIn("anti_exaggeration_penalty", criteria)
            self.assertIn("deduction_rules", criteria)
            self.assertIsInstance(criteria["deduction_rules"], list)
            self.assertGreaterEqual(len(criteria["deduction_rules"]), 1)

    def test_deduction_rules_completeness(self):
        """Ensures every deduction rule specifies condition, points, severity, and reason."""
        severities = {"FATAL", "HIGH", "MEDIUM", "LOW"}
        for r in self.r_data.get("rubrics", []):
            for rule in r["criteria"]["deduction_rules"]:
                self.assertIn("condition", rule)
                self.assertIn("deduction_points", rule)
                self.assertIsInstance(rule["deduction_points"], int)
                self.assertGreaterEqual(rule["deduction_points"], 1)
                self.assertIn("penalty_severity", rule)
                self.assertIn(rule["penalty_severity"], severities)
                self.assertIn("reason", rule)
                self.assertGreater(len(rule["reason"]), 5)


class TestEvidenceMatrixConsistencyWithManual(unittest.TestCase):
    """Cross-checks quantitative fact consistency between INTERVIEW_DEFENSE_MANUAL.md and evidence_matrix.json."""

    def setUp(self):
        self.assertTrue(MANUAL_PATH.is_file(), f"Missing manual at {MANUAL_PATH}")
        self.assertTrue(EVIDENCE_MATRIX_PATH.is_file(), f"Missing evidence matrix at {EVIDENCE_MATRIX_PATH}")

        self.manual_text = MANUAL_PATH.read_text(encoding="utf-8")
        with open(EVIDENCE_MATRIX_PATH, "r", encoding="utf-8") as f:
            self.matrix = json.load(f)

    def test_metric_01_ontotab_records_30000(self):
        """Asserts 30,000 records consistency."""
        matrix_records = self.matrix["verifiable_facts"]["research"]["ontotab"]["dataset"]["total_records"]
        self.assertEqual(matrix_records, 30000)
        self.assertIn("30,000", self.manual_text)

    def test_metric_02_ontotab_cv_5x3(self):
        """Asserts 5x3 nested CV consistency."""
        cv_str = self.matrix["verifiable_facts"]["research"]["ontotab"]["methodology"]["cross_validation"]
        self.assertIn("5x3", cv_str)
        outer = self.matrix["verifiable_facts"]["research"]["ontotab"]["methodology"]["outer_folds"]
        inner = self.matrix["verifiable_facts"]["research"]["ontotab"]["methodology"]["inner_folds"]
        self.assertEqual(outer, 5)
        self.assertEqual(inner, 3)
        self.assertTrue("5×3" in self.manual_text or "5x3" in self.manual_text)

    def test_metric_03_ontotab_bootstrap_2000(self):
        """Asserts 2,000 bootstrap resampling iterations consistency."""
        bootstrap = self.matrix["verifiable_facts"]["research"]["ontotab"]["methodology"]["bootstrap_iterations"]
        self.assertEqual(bootstrap, 2000)
        self.assertTrue("2,000" in self.manual_text or "2000" in self.manual_text)

    def test_metric_04_ontotab_xgboost_ap_05596(self):
        """Asserts 0.5596 AP on XGBoost numeric baseline consistency."""
        r8_ap = self.matrix["verifiable_facts"]["research"]["ontotab"]["empirical_metrics"]["r8_numeric_xgboost_ap"]
        self.assertAlmostEqual(r8_ap, 0.5596, places=4)
        self.assertIn("0.5596", self.manual_text)

    def test_metric_05_gbm_duration_13_weeks(self):
        """Asserts 13-week duration consistency."""
        weeks = self.matrix["verifiable_facts"]["experience"]["gbm"]["duration_weeks"]
        self.assertEqual(weeks, 13)
        self.assertTrue("13 semanas" in self.manual_text or "13 weeks" in self.manual_text)

    def test_metric_06_gbm_15_datastage_jobs(self):
        """Asserts 15 DataStage jobs consistency."""
        jobs = self.matrix["verifiable_facts"]["experience"]["gbm"]["deliverables"]["datastage_jobs"]["count"]
        self.assertEqual(jobs, 15)
        self.assertTrue("15 jobs DataStage" in self.manual_text or "15 jobs" in self.manual_text)

    def test_metric_07_ferrostats_zero_dollar_cost(self):
        """Asserts $0.00/mo operating cost on GCP consistency."""
        cost = self.matrix["verifiable_facts"]["projects"]["ferrostats"]["monthly_operating_cost_usd"]
        self.assertEqual(cost, 0.0)
        self.assertTrue("$0.00/mes" in self.manual_text or "$0.00/mo" in self.manual_text)

    def test_metric_08_sql_arena_136_tests(self):
        """Asserts 136 automated regression tests consistency."""
        tests = self.matrix["verifiable_facts"]["projects"]["sql_arena"]["test_suite_total_passing"]
        self.assertEqual(tests, 136)
        self.assertIn("136 tests", self.manual_text)

    def test_metric_09_sql_arena_3_of_34_solved(self):
        """Asserts 3/34 solved user problems consistency."""
        total = self.matrix["verifiable_facts"]["projects"]["sql_arena"]["curriculum_total_problems"]
        solved = self.matrix["verifiable_facts"]["projects"]["sql_arena"]["candidate_user_solved_problems"]
        self.assertEqual(total, 34)
        self.assertEqual(solved, 3)
        self.assertTrue("3 de 34" in self.manual_text or "3/34" in self.manual_text)

    def test_metric_10_ef_set_66_c1_listening_75(self):
        """Asserts EF SET certified score 66/100 and Listening 75/100 consistency."""
        score = self.matrix["verifiable_facts"]["certifications"]["ef_set_english"]["overall_score"]
        listening = self.matrix["verifiable_facts"]["certifications"]["ef_set_english"]["listening_score"]
        self.assertEqual(score, 66)
        self.assertEqual(listening, 75)
        self.assertIn("66/100", self.manual_text)
        self.assertIn("75", self.manual_text)

    def test_manual_contains_no_unbacked_senior_titles(self):
        """Asserts manual contains zero forbidden seniority self-attributions."""
        forbidden_regex = r"(?i)\b(?:Diego\s+is\s+a\s+Senior|as\s+a\s+Senior\s+Data\s+Engineer|fui\s+Senior\s+Data\s+Engineer)\b"
        self.assertIsNone(re.search(forbidden_regex, self.manual_text))


class TestGitParityMasterCvAndCoe(unittest.TestCase):
    """Verifies 100% file existence and SHA256 byte-parity between master_cv and coe skills."""

    def test_directory_existence(self):
        self.assertTrue(SKILL_DIR_MASTER.is_dir(), f"Missing {SKILL_DIR_MASTER}")
        self.assertTrue(SKILL_DIR_COE.is_dir(), f"Missing {SKILL_DIR_COE}")

    def test_sha256_byte_parity_all_files(self):
        """Computes SHA256 for every tracked file in master_cv skill and asserts identical hash in coe."""
        master_files = list(SKILL_DIR_MASTER.rglob("*"))
        file_count = 0

        for m_path in master_files:
            if m_path.is_file():
                # Ignore transient compiler artifacts
                if "__pycache__" in m_path.parts or m_path.suffix == ".pyc":
                    continue
                file_count += 1
                rel_path = m_path.relative_to(SKILL_DIR_MASTER)
                coe_path = SKILL_DIR_COE / rel_path

                self.assertTrue(
                    coe_path.is_file(),
                    f"File {rel_path} exists in master_cv but is missing in coe!"
                )

                m_hash = hashlib.sha256(m_path.read_bytes()).hexdigest()
                coe_hash = hashlib.sha256(coe_path.read_bytes()).hexdigest()

                self.assertEqual(
                    m_hash, coe_hash,
                    f"Hash mismatch on {rel_path}: master_cv={m_hash} != coe={coe_hash}"
                )

        self.assertGreaterEqual(file_count, 8, "Expected at least 8 files in skill directory")


class TestDrillRunnerAdversarialExecutions(unittest.TestCase):
    """Stress-tests scripts/drill_runner.py with bizarre inputs, unicode, massive payloads, and malicious strings."""

    def run_drill(self, args: list) -> subprocess.CompletedProcess:
        """Executes drill_runner.py in a subprocess with timeout."""
        cmd = [sys.executable, str(DRILL_RUNNER_PATH)] + args
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            encoding="utf-8"
        )

    def test_drill_empty_string_answer(self):
        """Stress: empty answer string does not crash and handles gracefully."""
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", ""])
        # Should exit 0 or 1, but must NOT crash with traceback or unhandled exception
        self.assertNotIn("Traceback", res.stderr)
        self.assertNotIn("Exception", res.stderr)

    def test_drill_whitespace_only_answer(self):
        """Stress: whitespace-only answer does not crash."""
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", "   \t\n\r  "])
        self.assertNotIn("Traceback", res.stderr)
        self.assertNotIn("Exception", res.stderr)

    def test_drill_unicode_emojis_and_special_chars(self):
        """Stress: answer with emojis, unicode accents, and control sequences."""
        weird_answer = (
            "Situation: En OntoTab 🤖🚀, evalué 30,000 registros de crédito (UCI Taiwán) con ñoño y café. "
            "Task: Actividad E01 bajo dirección de Joaquín Solórzano, como second author (2.º de 7). "
            "Action: 5x3 nested CV y 2,000 bootstrap iterations con BGE-M3 d=1,024 y XGBoost. "
            "Result: Logré 0.5596 AP numérico superando al texto ontológico."
        )
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", weird_answer])
        self.assertNotIn("Traceback", res.stderr)
        self.assertEqual(res.returncode, 0, f"Expected PASS (0), got {res.returncode}. Stderr: {res.stderr}")
        self.assertIn("VERIFIED STAR DEFENSE", res.stdout)
        self.assertIn("5/5", res.stdout)

    def test_drill_massive_payload_stress_and_performance(self):
        """Stress: 10,000-char payload via CLI (within Win32 32k limit) and 100,000-char in-memory without ReDoS."""
        # 1. Test CLI execution with 10,000 characters (realistic large answer fitting Windows CLI limit)
        filler_cli = "We executed rigorous data validation steps. " * 200  # ~9,000 chars
        cli_answer = (
            "Situation: In OntoTab, we evaluated 30,000 credit records. " +
            filler_cli +
            "Task: As second author on E01, " +
            "Action: ran 5x3 nested CV with 2,000 bootstrap iterations. " +
            "Result: 0.5596 AP was achieved."
        )
        t0 = time.time()
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", cli_answer])
        duration_cli = time.time() - t0

        self.assertLess(duration_cli, 3.0, f"CLI massive payload took too long ({duration_cli:.2f}s)")
        self.assertNotIn("Traceback", res.stderr)
        self.assertEqual(res.returncode, 0)
        self.assertIn("VERIFIED STAR DEFENSE", res.stdout)

        # 2. Test in-memory regex execution on 100,000 characters to verify zero ReDoS
        sys.path.insert(0, str(DRILL_RUNNER_PATH.parent))
        import drill_runner
        filler_mem = "Extensive experimentation across multiple benchmarks. " * 2000  # ~110,000 chars
        mem_answer = (
            "Situation: In OntoTab, we evaluated 30,000 credit records. " +
            filler_mem +
            "Task: As second author on E01, " +
            "Action: ran 5x3 nested CV with 2,000 bootstrap iterations. " +
            "Result: 0.5596 AP was achieved."
        )
        t1 = time.time()
        is_pass, score, passes, violations = drill_runner.evaluate_candidate_answer(mem_answer)
        duration_mem = time.time() - t1

        self.assertLess(duration_mem, 1.0, f"100k memory payload took {duration_mem:.2f}s - possible ReDoS!")
        self.assertTrue(is_pass)
        self.assertEqual(score, 5)

    def test_drill_catches_lead_author_exaggeration(self):
        """Adversarial: claims 'lead author' on OntoTab -> FATAL disqualification."""
        toxic = "Situation: On OntoTab, I was the Lead Author. Task: I directed all 7 authors. Action: E01. Result: 0.5596."
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("CRITICAL ETHICAL PENALTY", res.stdout)
        self.assertIn("0/5", res.stdout)
        self.assertIn("lead author", res.stdout.lower())

    def test_drill_catches_first_author_exaggeration(self):
        """Adversarial: claims 'first author' on OntoTab -> FATAL disqualification."""
        toxic = "Situation: OntoTab research. Task: I was the first author of the paper. Action: 5x3 CV. Result: 0.5596."
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)

    def test_drill_catches_principal_investigator_exaggeration(self):
        """Adversarial: claims 'principal investigator' -> FATAL disqualification."""
        toxic = "Situation: I acted as principal investigator on OntoTab. Task: E01. Action: 30,000. Result: 0.5596."
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)

    def test_drill_catches_senior_data_engineer_inflation(self):
        """Adversarial: claims 'Senior Data Engineer' at GBM -> FATAL disqualification."""
        toxic = "Situation: As a Senior Data Engineer at GBM, I delivered 15 jobs DataStage. Task: DB2 on RHEL. Action: ELT. Result: Success."
        res = self.run_drill(["--persona", "behavioral", "--project", "gbm", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)
        self.assertIn("Senior Data Engineer", res.stdout)

    def test_drill_catches_staff_data_engineer_inflation(self):
        """Adversarial: claims 'Staff Data Engineer' -> FATAL disqualification."""
        toxic = "Situation: Working as Staff Data Engineer at GBM. Task: 15 jobs DataStage. Action: DB2. Result: Done."
        res = self.run_drill(["--persona", "behavioral", "--project", "gbm", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)

    def test_drill_catches_ml_engineer_title_inflation(self):
        """Adversarial: claims 'Machine Learning Engineer' on OntoTab -> FATAL disqualification."""
        toxic = "Situation: As Machine Learning Engineer on OntoTab, I led E01 with 30,000 records. Task: E01. Action: 5x3. Result: 0.5596."
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)

    def test_drill_catches_published_in_ieee_fabrication(self):
        """Adversarial: claims 'published in IEEE' -> FATAL disqualification."""
        toxic = "Situation: OntoTab was published in IEEE. Task: E01 second author. Action: 30,000 records. Result: 0.5596 AP."
        res = self.run_drill(["--persona", "technical", "--project", "ontotab", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)

    def test_drill_catches_95_efset_exaggeration(self):
        """Adversarial: claims '95/100' on EF SET -> FATAL disqualification."""
        toxic = "Situation: Certified English. Task: EF SET test. Action: scored 95/100. Result: Fluent."
        res = self.run_drill(["--persona", "auditor", "--project", "gbm", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)

    def test_drill_catches_sql_arena_34_of_34_solved(self):
        """Adversarial: claims 'solved all 34' or '34/34' on SQL Arena -> FATAL disqualification."""
        toxic1 = "Situation: SQL Arena. Task: Testing. Action: I completed all 34 exercises. Result: 136 tests."
        res1 = self.run_drill(["--persona", "technical", "--project", "sql_arena", "--eval-answer", toxic1])
        self.assertEqual(res1.returncode, 1)
        self.assertIn("0/5", res1.stdout)

        toxic2 = "Situation: SQL Arena. Task: Solved 34/34 problems. Action: React 19. Result: 136 tests."
        res2 = self.run_drill(["--persona", "technical", "--project", "sql_arena", "--eval-answer", toxic2])
        self.assertEqual(res2.returncode, 1)
        self.assertIn("0/5", res2.stdout)

    def test_drill_catches_ferrostats_commercial_startup_fabrication(self):
        """Adversarial: claims FERROSTATS is a commercial startup with paying customers -> FATAL disqualification."""
        toxic = "Situation: FERROSTATS commercial startup. Task: We have paying customers and $10k ARR. Action: BigQuery. Result: $0.00/mes."
        res = self.run_drill(["--persona", "executive", "--project", "ferrostats", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)

    def test_drill_catches_permanent_gbm_tenure_fabrication(self):
        """Adversarial: claims permanent position at GBM -> FATAL disqualification."""
        toxic = "Situation: I had a permanent position at GBM. Task: 15 jobs DataStage. Action: DB2. Result: Done."
        res = self.run_drill(["--persona", "behavioral", "--project", "gbm", "--eval-answer", toxic])
        self.assertEqual(res.returncode, 1)
        self.assertIn("0/5", res.stdout)

    def test_drill_dry_run_all_personas_and_projects(self):
        """Verifies --dry-run prints question and returns 0 across personas and projects."""
        personas = ["recruiter", "tech_lead", "ml_researcher", "auditor", "behavioral", "executive", "technical"]
        projects = ["ontotab", "gbm", "ferrostats", "sql_arena", "sql-arena"]

        for p in personas:
            res = self.run_drill(["--persona", p, "--dry-run"])
            self.assertEqual(res.returncode, 0, f"Failed dry-run for persona {p}: {res.stderr}")
            self.assertIn("INTERVIEW DEFENSE DRILL", res.stdout)

        for proj in projects:
            res = self.run_drill(["--project", proj, "--dry-run"])
            self.assertEqual(res.returncode, 0, f"Failed dry-run for project {proj}: {res.stderr}")
            self.assertIn("INTERVIEW DEFENSE DRILL", res.stdout)

    def test_drill_cli_invalid_arguments_rejected(self):
        """CLI boundaries: unrecognized flags or invalid choices exit non-zero without unhandled exceptions."""
        res_bad_flag = self.run_drill(["--nonexistent-flag-xyz"])
        self.assertNotEqual(res_bad_flag.returncode, 0)
        self.assertIn("unrecognized arguments", res_bad_flag.stderr)

        res_bad_persona = self.run_drill(["--persona", "bogus_persona", "--dry-run"])
        self.assertNotEqual(res_bad_persona.returncode, 0)
        self.assertIn("invalid choice", res_bad_persona.stderr)

        res_bad_proj = self.run_drill(["--project", "bogus_project", "--dry-run"])
        self.assertNotEqual(res_bad_proj.returncode, 0)
        self.assertIn("invalid choice", res_bad_proj.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)

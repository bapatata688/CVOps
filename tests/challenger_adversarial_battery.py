#!/usr/bin/env python3
"""challenger_adversarial_battery.py - Challenger 1 Empirical Stress Test Suite

Adversarially challenges Milestone 3 deliverables:
1. drill_runner.py:
   - CLI flags, edge cases, missing arguments, invalid arguments
   - Truthful answers vs toxic answers (Senior Data Engineer, Lead Author, 95% accuracy, published in IEEE, 34/34 solved, etc.)
   - All personas and all projects
   - Empty and whitespace answers
2. DECISION_LOG.md:
   - Schema validation via parse_decision_log and validate_decision_log_entries
   - Verification that all 8 mandatory fields exist and are non-empty for LOG-001..LOG-004
   - Fuzzing & stress test of parser robustness with malformed markdown
3. INTERVIEW_DEFENSE_MANUAL.md:
   - Inspection against scan_forbidden_claims
   - Verification that any matches occur solely within explicit PROHIBIDO / containment contexts
4. Full test suite verification:
   - Zero failures, zero regressions
"""

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tests.test_harness_utils import (
    MANDATORY_DECISION_LOG_FIELDS,
    parse_decision_log,
    run_command_safe,
    scan_forbidden_claims,
    validate_decision_log_entries,
)

DRILL_RUNNER_PATH = REPO_ROOT / ".agents" / "skills" / "cv-interview-defense" / "scripts" / "drill_runner.py"
DECISION_LOG_PATH = REPO_ROOT / "docs" / "DECISION_LOG.md"
DEFENSE_MANUAL_PATH = REPO_ROOT / "docs" / "INTERVIEW_DEFENSE_MANUAL.md"
QUESTIONS_DB_PATH = REPO_ROOT / ".agents" / "skills" / "cv-interview-defense" / "resources" / "questions_db.json"
RUBRICS_PATH = REPO_ROOT / ".agents" / "skills" / "cv-interview-defense" / "resources" / "evaluation_rubrics.json"


class ChallengerMilestone3AdversarialSuite(unittest.TestCase):
    """Authoritative empirical verification tests for Milestone 3."""

    # =========================================================================
    # AREA 1: drill_runner.py Adversarial Verification
    # =========================================================================

    def test_area1_01_missing_flags_and_default_execution(self):
        """Area 1: drill_runner.py without flags exits 0 with informational readiness message."""
        res = run_command_safe([sys.executable, str(DRILL_RUNNER_PATH)], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 0, f"Expected 0 exit, got {res.returncode}: {res.stderr}")
        self.assertIn("Interview defense prompter ready", res.stdout)
        self.assertIn("--dry-run", res.stdout)
        self.assertIn("--eval-answer", res.stdout)

    def test_area1_02_invalid_flags_exit_nonzero(self):
        """Area 1: drill_runner.py with unrecognized flags exits non-zero."""
        bad_flags = [
            ["--nonexistent-flag"],
            ["--invalid-option-xyz", "val"],
            ["-z"],
            ["--help-me"],
        ]
        for flags in bad_flags:
            with self.subTest(flags=flags):
                res = run_command_safe([sys.executable, str(DRILL_RUNNER_PATH)] + flags, cwd=REPO_ROOT)
                self.assertNotEqual(res.returncode, 0, f"Expected non-zero exit for {flags}")
                self.assertIn("unrecognized argument", res.stderr.lower())

    def test_area1_03_invalid_choices_exit_nonzero(self):
        """Area 1: Invalid choices for --persona and --project are rejected by argparse."""
        res_persona = run_command_safe(
            [sys.executable, str(DRILL_RUNNER_PATH), "--persona", "god_mode", "--dry-run"],
            cwd=REPO_ROOT
        )
        self.assertNotEqual(res_persona.returncode, 0)
        self.assertIn("invalid choice", res_persona.stderr.lower())

        res_project = run_command_safe(
            [sys.executable, str(DRILL_RUNNER_PATH), "--project", "unreal_engine", "--dry-run"],
            cwd=REPO_ROOT
        )
        self.assertNotEqual(res_project.returncode, 0)
        self.assertIn("invalid choice", res_project.stderr.lower())

    def test_area1_04_dry_run_all_personas_and_projects(self):
        """Area 1: Exhaustive combination of all allowed personas and projects in dry-run mode."""
        personas = ["recruiter", "tech_lead", "ml_researcher", "auditor", "technical", "behavioral", "executive"]
        projects = ["ontotab", "gbm", "ferrostats", "sql_arena", "sql-arena"]

        for persona in personas:
            for project in projects:
                with self.subTest(persona=persona, project=project):
                    res = run_command_safe(
                        [sys.executable, str(DRILL_RUNNER_PATH), "--persona", persona, "--project", project, "--dry-run"],
                        cwd=REPO_ROOT
                    )
                    self.assertEqual(res.returncode, 0, f"Failed dry run for {persona}/{project}: {res.stderr}")
                    self.assertIn("INTERVIEW DEFENSE DRILL", res.stdout)
                    self.assertIn("Question", res.stdout)
                    self.assertIn("Approach (STAR)", res.stdout)

    def test_area1_05_toxic_claims_rejected_with_fatal_penalty(self):
        """Area 1: Every toxic/unbacked claim receives fatal penalty FAIL and exit code 1."""
        toxic_cases = [
            ("Senior Data Engineer title", "Situation: I worked as a Senior Data Engineer at GBM leading data pipeline architecture. Task: ETL. Action: BigQuery. Result: Success."),
            ("Lead Data Engineer title", "Situation: At GBM I served as Lead Data Engineer. Task: DataStage. Action: 15 jobs. Result: Done."),
            ("Staff Data Engineer title", "Situation: Staff Data Engineer directing lakehouse. Task: FERROSTATS. Action: Medallion. Result: $0.00/mes."),
            ("Machine Learning Engineer inflation", "Situation: As a Machine Learning Engineer on OntoTab, I implemented 5x3 CV. Task: E01. Action: XGBoost. Result: 0.5596 AP."),
            ("ML Engineer inflation", "Situation: Worked as ML Engineer at GBM. Task: AI. Action: PyTorch. Result: Mini-Qwen3."),
            ("Lead Author on OntoTab", "Situation: In OntoTab research, I was the Lead Author directing the group. Task: E01. Action: Nested CV. Result: 0.5596 AP."),
            ("First Author on OntoTab", "Situation: OntoTab paper. Task: As first author, I submitted the manuscript. Action: XGBoost. Result: 0.5596."),
            ("Principal Investigator claim", "Situation: I was the principal investigator for OntoTab study. Task: Credit risk. Action: UCI data. Result: 0.5596."),
            ("95% accuracy metric fabrication", "Situation: In OntoTab we benchmarked 30,000 credit records. Task: E01. Action: XGBoost. Result: Achieved 95% accuracy."),
            ("Published in IEEE fabrication", "Situation: Our OntoTab study was published in IEEE Transactions. Task: E01. Action: 5x3 CV. Result: 0.5596 AP."),
            ("Peer-reviewed publication fabrication", "Situation: We have a peer-reviewed publication on OntoTab. Task: E01. Action: BGE-M3. Result: 0.5596 AP."),
            ("SQL Arena 34/34 solved claim", "Situation: SQL Arena platform. Task: Practice. Action: Solved 34/34 problems. Result: 136 tests passed."),
            ("SQL Arena solved all 34 claim", "Situation: SQL Arena. Task: Solved all 34 SQL challenges. Action: MySQL 8. Result: Mastery."),
            ("EF SET 95/100 score claim", "Situation: English certification. Task: EF SET exam. Action: Took 50-minute test. Result: Scored 95/100 C2."),
            ("Commercial startup claim", "Situation: FERROSTATS commercial startup. Task: Growing business. Action: Cloud Run. Result: Paying customers with MRR."),
            ("Permanent position at GBM claim", "Situation: Held a permanent position at GBM. Task: 15 jobs DataStage. Action: DB2 LUW. Result: High performance."),
            ("Exaggerated GBM duration (8 months)", "Situation: During my 8 months at GBM. Task: Data engineering. Action: DataStage. Result: 15 jobs."),
        ]

        for label, toxic_text in toxic_cases:
            with self.subTest(label=label):
                res = run_command_safe(
                    [sys.executable, str(DRILL_RUNNER_PATH), "--persona", "technical", "--project", "ontotab", "--eval-answer", toxic_text],
                    cwd=REPO_ROOT
                )
                self.assertEqual(res.returncode, 1, f"Expected non-zero exit code for '{label}', got {res.returncode}")
                self.assertIn("VERDICT: [FAIL]", res.stdout)
                self.assertIn("CRITICAL ETHICAL PENALTY", res.stdout)
                self.assertIn("0/5", res.stdout)

    def test_area1_06_truthful_star_answers_receive_pass_and_full_score(self):
        """Area 1: Truthful, factual answers across all 4 projects receive PASS verdict and 5/5 score."""
        truthful_answers = [
            (
                "ontotab",
                "Situation: In the OntoTab scientific study, we evaluated ontology text enrichment on 30,000 credit records from UCI Taiwan. "
                "Task: As second author under AI Lead Joaquín Solórzano, I was tasked with leading Activity E01 for structured numerical baselines. "
                "Action: Evaluated XGBoost and Logistic Regression under 5x3 nested cross-validation and 2,000 paired bootstrap resamples. "
                "Result: Achieved 0.5596 AP on XGBoost numeric baseline, outperforming ontology embeddings by +0.0527 AP without marginal gain from verbalized text."
            ),
            (
                "gbm",
                "Situation: During my 13-week internship as Digital Solutions Specialist Intern at GBM (July - October 2026), enterprise data pipelines required modernization. "
                "Task: Develop ETL jobs in DataStage and administer IBM DB2 LUW on Red Hat Enterprise Linux. "
                "Action: Authored and deployed 15 DataStage jobs with transformers and joins, and co-designed a GCP ELT architecture with BigQuery and Dataform. "
                "Result: Zero data loss across all 15 jobs, 100% adherence to customer specifications, and formal commendation letter."
            ),
            (
                "ferrostats",
                "Situation: Cloud-native medallion lakehouses often suffer from high idle costs in small-to-medium enterprise contexts. "
                "Task: Engineer an open-source Medallion Lakehouse on GCP with <50 ms edge latency and strict cost discipline. "
                "Action: Built REST API ingestion, Dataform Silver staging views, and 3 Gold star schema marts with Pareto ABC analytics. "
                "Result: Attained <50 ms edge latency and verified operational cost of $0.00/mo on GCP using serverless scale-to-zero."
            ),
            (
                "sql_arena",
                "Situation: Technical interview candidates need realistic, isolated database sandboxing to master complex SQL patterns. "
                "Task: Architect a LeetCode-style local SQL platform with deterministic test runners. "
                "Action: Engineered an in-memory ExecutionMutex to serialize InnoDB resets and designed 34 curriculum problems with 136 tests. "
                "Result: All 136 tests pass with 100% determinism; as a user, my telemetry shows 3/34 problems solved."
            ),
        ]

        for project, answer in truthful_answers:
            with self.subTest(project=project):
                res = run_command_safe(
                    [sys.executable, str(DRILL_RUNNER_PATH), "--persona", "technical", "--project", project, "--eval-answer", answer],
                    cwd=REPO_ROOT
                )
                self.assertEqual(res.returncode, 0, f"Expected exit code 0 for {project}, got {res.returncode}: {res.stderr}")
                self.assertIn("VERDICT: [PASS]", res.stdout)
                self.assertIn("5/5", res.stdout)
                self.assertIn("STAR Structure", res.stdout)

    def test_area1_07_empty_and_whitespace_answers_do_not_crash(self):
        """Area 1: Empty and whitespace strings handled safely without uncaught exceptions or tracebacks."""
        for empty_val in ["", "   ", "\t\n\r"]:
            with self.subTest(val=repr(empty_val)):
                res = run_command_safe(
                    [sys.executable, str(DRILL_RUNNER_PATH), "--persona", "technical", "--eval-answer", empty_val],
                    cwd=REPO_ROOT
                )
                self.assertNotIn("Traceback", res.stderr)
                self.assertNotIn("Exception", res.stderr)

    # =========================================================================
    # AREA 2: docs/DECISION_LOG.md Adversarial Verification
    # =========================================================================

    def test_area2_01_decision_log_entries_parsed_and_count(self):
        """Area 2: DECISION_LOG.md exists and parses all 4 required entries LOG-001..LOG-004."""
        self.assertTrue(DECISION_LOG_PATH.is_file(), f"Missing {DECISION_LOG_PATH}")
        entries = parse_decision_log(DECISION_LOG_PATH)
        self.assertEqual(len(entries), 4, f"Expected exactly 4 entries in DECISION_LOG.md, got {len(entries)}")
        entry_ids = [e["entry_id"] for e in entries]
        self.assertEqual(entry_ids, ["LOG-001", "LOG-002", "LOG-003", "LOG-004"])

    def test_area2_02_all_eight_mandatory_fields_exist_and_non_empty(self):
        """Area 2: Every single entry in DECISION_LOG.md contains all 8 mandatory fields, non-empty."""
        entries = parse_decision_log(DECISION_LOG_PATH)
        valid, errors = validate_decision_log_entries(entries)
        self.assertTrue(valid, f"Validation errors in DECISION_LOG.md: {errors}")

        for entry in entries:
            eid = entry["entry_id"]
            for field in MANDATORY_DECISION_LOG_FIELDS:
                val = entry.get(field, "")
                self.assertIsInstance(val, str, f"{eid} field {field} is not a string")
                self.assertGreater(len(val.strip()), 0, f"{eid} mandatory field '{field}' is empty or whitespace!")
                self.assertNotIn("[TODO]", val, f"{eid} contains placeholder [TODO] in '{field}'")
                self.assertNotIn("[TBD]", val, f"{eid} contains placeholder [TBD] in '{field}'")

            # Validate ISO 8601 timestamp
            ts = entry["timestamp"]
            iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?$"
            self.assertRegex(ts, iso_pattern, f"{eid} timestamp '{ts}' does not match ISO 8601")

    def test_area2_03_parser_fuzzing_and_malformed_markdown_resilience(self):
        """Area 2: parse_decision_log does not crash when fed adversarial/malformed markdown."""
        adversarial_markdown_samples = [
            "",  # completely empty
            "   \n\t\n  \r\n",  # whitespace only
            "# Random Header\nParagraph with no entries.\n",  # no entries
            "## LOG-9999\nMalformed without subheaders\n",  # heading only
            "## LOG-001 - Title\n- **Timestamp**: invalid\n- **Component**: c\n### Problem Statement\n### Root Cause Analysis\n",  # empty sections
            "## [LOG-001] – Title with unicode em-dash — and emojis 🚀\n- **Timestamp**: 2026-11-11T00:00:00Z\n- **Component**: comp\n### Problem Statement\nps\n### Root Cause Analysis\nrc\n### Alternatives Evaluated\nalt\n### Chosen Solution\ncs\n### Rationale\nrat\n",  # unicode & emojis
            "## LOG-001: Duplicate\n- **Timestamp**: 2026-11-11T00:00:00Z\n- **Component**: c\n### Problem Statement\np\n### Root Cause Analysis\nr\n### Alternatives Evaluated\na\n### Chosen Solution\ns\n### Rationale\nrat\n## LOG-001: Duplicate 2\n- **Timestamp**: 2026-11-11T00:00:00Z\n- **Component**: c\n### Problem Statement\np\n### Root Cause Analysis\nr\n### Alternatives Evaluated\na\n### Chosen Solution\ns\n### Rationale\nrat\n",  # duplicate IDs
        ]

        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / "fuzz_log.md"
            for idx, sample in enumerate(adversarial_markdown_samples):
                with self.subTest(sample_idx=idx):
                    tmp_path.write_text(sample, encoding="utf-8")
                    try:
                        parsed = parse_decision_log(tmp_path)
                        self.assertIsInstance(parsed, list)
                        valid, errs = validate_decision_log_entries(parsed)
                        self.assertIsInstance(valid, bool)
                        self.assertIsInstance(errs, list)
                    except Exception as e:
                        self.fail(f"parse_decision_log crashed on sample {idx}: {type(e).__name__}: {e}")

    # =========================================================================
    # AREA 3: docs/INTERVIEW_DEFENSE_MANUAL.md Prohibited Claims Verification
    # =========================================================================

    def test_area3_01_defense_manual_prohibited_claims_strictly_contained(self):
        """Area 3: All forbidden patterns found in INTERVIEW_DEFENSE_MANUAL.md are strictly in prohibition or historical errata contexts."""
        self.assertTrue(DEFENSE_MANUAL_PATH.is_file(), f"Missing {DEFENSE_MANUAL_PATH}")
        raw_text = DEFENSE_MANUAL_PATH.read_text(encoding="utf-8")
        lines = raw_text.splitlines()

        violations = scan_forbidden_claims(DEFENSE_MANUAL_PATH)
        self.assertGreater(len(violations), 0, "Expected defense manual to mention prohibited claims in its warning sections.")

        # Keywords that indicate containment, prohibition, historical errata explanation, or interviewer audit question
        legitimate_contexts = [
            "PROHIBIDO", "prohibido", "Prohibición", "Regla de Oro de Contención",
            "prohibición de inflación", "prohibido estrictamente", "No asumir títulos",
            "Retiro definitivo del error histórico", "purgó el typo de borrador", "anti-patrones",
            "Pregunta AUD-01", "borradores anteriores", "errata tipográfica", "draft typo",
            "purga total de la cifra", "GLOBAL-FORBID-001", "Declaraciones Prohibidas",
            "errata de borrador eliminada"
        ]

        unauthorized_leaks = []
        for v in violations:
            line_idx = v["line_number"] - 1
            line_text = lines[line_idx]

            # Context window: check current line and up to 5 preceding lines
            context_window = lines[max(0, line_idx - 5):line_idx + 1]
            context_joined = " ".join(context_window)

            is_legitimate_context = any(m.lower() in context_joined.lower() for m in legitimate_contexts)

            if not is_legitimate_context:
                unauthorized_leaks.append({
                    "line": v["line_number"],
                    "matched": v["matched_text"],
                    "text": line_text.strip(),
                    "reason": v["reason"]
                })

        self.assertEqual(
            unauthorized_leaks, [],
            f"Found forbidden claim outside explicit PROHIBIDO context in INTERVIEW_DEFENSE_MANUAL.md:\n" +
            "\n".join(f"  Line {leak['line']}: [{leak['matched']}] in '{leak['text']}'" for leak in unauthorized_leaks)
        )

    def test_area3_02_defense_manual_contains_all_core_truth_anchors(self):
        """Area 3: Manual explicitly documents all verified numbers and factual anchors."""
        content = DEFENSE_MANUAL_PATH.read_text(encoding="utf-8")
        anchors = [
            ("30,000", "OntoTab dataset count"),
            ("0.5596", "OntoTab numeric XGBoost AP"),
            ("5×3", "OntoTab nested CV"),
            ("2,000", "OntoTab bootstrap resamples"),
            ("13 semanas", "GBM internship duration"),
            ("15 jobs DataStage", "GBM ETL jobs deliverable"),
            ("IBM DB2 LUW", "GBM database"),
            ("Red Hat Enterprise Linux", "GBM OS"),
            ("$0.00/mes", "FERROSTATS FinOps zero cost"),
            ("136 tests", "SQL Arena test suite"),
            ("3 de 34", "SQL Arena user solved telemetry"),
            ("66/100", "EF SET overall certified score"),
            ("75/100", "EF SET listening C2 score"),
            ("Term 3, 2027", "UoPeople formal admission"),
        ]
        for anchor, label in anchors:
            with self.subTest(anchor=anchor, label=label):
                self.assertIn(anchor, content, f"Missing verified anchor '{anchor}' ({label}) in INTERVIEW_DEFENSE_MANUAL.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)

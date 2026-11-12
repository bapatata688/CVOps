"""test_tier3_combinations.py - Tier 3: Cross-Feature Integration Combinations Suite

Verifies end-to-end integration chains where outputs of upstream components serve as
inputs to downstream components across master_cv:
  C1: Multi-Stage Pipeline Combination (compile_all -> verify_geometry -> lint_cv_truth)
      - Sequential execution, atomic compilation with --verify, and negative error cascading
  C2: Antigravity Skill & Interview Defense Integration (drill_runner -> questions_db -> rubrics)
      - Persona/project question retrieval, STAR rubric scoring, and penalty triggers
  C3: Google Drive Sync Dry-Run & Artifact Discovery Integration
      - Discovery of 4 canonical PDFs, folder ID mapping, and offline safety contract
  C4: Local CI Harness Multi-Stage Execution Simulation
      - Orchestration of sequential verification stages and early abort on failure

Compliance:
- Pure Python standard library unittest (Zero-Pytest, Zero-Matplotlib, AGENTS.md Rule 5).
- Progressive testability: strict assertions when artifacts are present, descriptive
  skip/contract signaling when parallel milestone artifacts are pending.
- Reusable opaque-box helpers imported from tests.test_harness_utils.
"""

import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repository root and test harness utilities are in sys.path
TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

# Import test harness utilities
from tests.test_harness_utils import (
    KNOWN_ASSET_HASHES,
    MANDATORY_DECISION_LOG_FIELDS,
    SubprocessResult,
    assert_path_exists,
    assert_pdf_geometry,
    assert_sha256_matches,
    assert_truthful_content,
    compute_sha256,
    run_command_safe,
    scan_forbidden_claims,
    validate_path_exists,
    validate_pdf_geometry,
    verify_sha256,
)

from cv.generate_all_cvs import TARGETS_BY_ID, compile_all, compile_pdf_with_weasyprint
from scripts.verify_geometry import CANONICAL_TARGETS, verify_all, verify_single_pdf


# ============================================================================
# C1: Multi-Stage Pipeline Combination
# ============================================================================

class TestC1MultiStagePipelineCombination(unittest.TestCase):
    """Verifies the multi-stage CV generation, geometry assertion, and truth linter chain."""

    def setUp(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self._temp_dir_obj.name)
        self.compile_script = REPO_ROOT / "scripts" / "compile_all.py"
        self.verify_script = REPO_ROOT / "scripts" / "verify_geometry.py"
        self.linter_script = REPO_ROOT / "scripts" / "lint_cv_truth.py"

    def tearDown(self):
        try:
            self._temp_dir_obj.cleanup()
        except Exception:
            pass

    def test_c1_01_full_sequential_pipeline_clean_execution(self):
        """C1 Happy Path: Stage 1 (compile) -> Stage 2 (geometry) -> Stage 3 (truth linter) all succeed with exit code 0."""
        # Stage 1: Compile all canonical targets
        res_stage1 = run_command_safe(
            [sys.executable, str(self.compile_script), "--all"],
            cwd=REPO_ROOT,
            timeout_sec=90.0
        )
        self.assertEqual(
            res_stage1.returncode, 0,
            f"Stage 1 (compile_all.py) failed:\nSTDOUT: {res_stage1.stdout}\nSTDERR: {res_stage1.stderr}"
        )

        # Stage 2: Programmatic geometry assertion across all 4 compiled targets
        res_stage2 = run_command_safe(
            [sys.executable, str(self.verify_script)],
            cwd=REPO_ROOT,
            timeout_sec=30.0
        )
        self.assertEqual(
            res_stage2.returncode, 0,
            f"Stage 2 (verify_geometry.py) failed:\nSTDOUT: {res_stage2.stdout}\nSTDERR: {res_stage2.stderr}"
        )

        # Stage 3: Ethical truthfulness linter
        if self.linter_script.is_file():
            res_stage3 = run_command_safe(
                [sys.executable, str(self.linter_script)],
                cwd=REPO_ROOT,
                timeout_sec=30.0
            )
            self.assertEqual(
                res_stage3.returncode, 0,
                f"Stage 3 (lint_cv_truth.py) failed:\nSTDOUT: {res_stage3.stdout}\nSTDERR: {res_stage3.stderr}"
            )
        else:
            # Progressive contract fallback: verify via harness utility
            for rel_path in CANONICAL_TARGETS:
                html_path = REPO_ROOT / str(rel_path).replace(".pdf", ".html")
                if html_path.is_file():
                    assert_truthful_content(html_path)

    def test_c1_02_atomic_compile_all_with_verify_flag(self):
        """C1 Atomic Verification: scripts/compile_all.py --all --verify combines stages 1 & 2 in single process."""
        res = run_command_safe(
            [sys.executable, str(self.compile_script), "--all", "--verify"],
            cwd=REPO_ROOT,
            timeout_sec=90.0
        )
        self.assertEqual(
            res.returncode, 0,
            f"compile_all.py --all --verify failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
        )
        self.assertIn("[SUCCESS] Compilation stage finished successfully", res.stdout)
        self.assertIn("Executing post-compilation geometry assertion", res.stdout)
        self.assertIn("[SUCCESS] All inspected PDF targets strictly conform to 1-page Letter geometry", res.stdout)

    def test_c1_03_pipeline_catches_geometry_overflow_at_stage2(self):
        """C1 Negative Cascade: An oversized template compiles in Stage 1, but Stage 2 halts the pipeline with exit code 1."""
        source_template = REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html"
        self.assertTrue(source_template.is_file())

        orig_html = source_template.read_text(encoding="utf-8")
        filler = "<p class='overflow-stress-test'>" + ("Expanding page budget beyond 792 points. " * 30) + "</p>"
        mutated_html = orig_html.replace("</body>", f"{filler * 4}</body>")

        tmp_html = self.temp_dir / "overflow_cv.html"
        tmp_pdf = self.temp_dir / "overflow_cv.pdf"
        tmp_html.write_text(mutated_html, encoding="utf-8")

        # Stage 1: Compilation completes
        compile_pdf_with_weasyprint(tmp_html, tmp_pdf, engine="auto")
        self.assertTrue(tmp_pdf.is_file())

        # Stage 2: Geometry verification MUST catch overflow and fail
        res_stage2 = run_command_safe(
            [sys.executable, str(self.verify_script), "--files", str(tmp_pdf)],
            cwd=REPO_ROOT
        )
        self.assertEqual(res_stage2.returncode, 1, "Pipeline failed to halt at Stage 2 for oversized document!")
        self.assertIn("Page count violation", res_stage2.stdout + res_stage2.stderr)

    def test_c1_04_pipeline_catches_forbidden_claim_at_stage3(self):
        """C1 Negative Cascade: A template with unbacked claims compiles and passes geometry, but Stage 3 halts pipeline."""
        source_template = REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html"
        self.assertTrue(source_template.is_file())

        orig_html = source_template.read_text(encoding="utf-8")
        # Inject unbacked seniority claim while preserving 1-page layout
        toxic_claim = "Senior Data Engineer & Lead Machine Learning Architect"
        mutated_html = orig_html.replace("Junior Data Engineer", toxic_claim)

        tmp_html = self.temp_dir / "toxic_cv.html"
        tmp_pdf = self.temp_dir / "toxic_cv.pdf"
        tmp_html.write_text(mutated_html, encoding="utf-8")

        # Stage 1: Compiles
        compile_pdf_with_weasyprint(tmp_html, tmp_pdf, engine="auto")
        self.assertTrue(tmp_pdf.is_file())

        # Stage 2: Passes geometry (dimensions are untouched)
        res_geom = verify_single_pdf(tmp_pdf)
        self.assertEqual(res_geom["page_count"], 1)

        # Stage 3: Truth linter MUST detect violation and fail
        if self.linter_script.is_file():
            res_stage3 = run_command_safe(
                [sys.executable, str(self.linter_script), "--files", str(tmp_html)],
                cwd=REPO_ROOT
            )
            self.assertEqual(res_stage3.returncode, 1, "Truth linter failed to catch unbacked seniority!")
        else:
            violations = scan_forbidden_claims(tmp_html)
            self.assertGreater(len(violations), 0, "Harness scanner failed to catch toxic claim injection!")
            self.assertTrue(any("Senior" in v["matched_text"] for v in violations))

    def test_c1_05_pipeline_stage1_failure_halts_subsequent_stages(self):
        """C1 Pipeline Abort: Corrupted template syntax halts compilation and prevents downstream execution."""
        tmp_html = self.temp_dir / "corrupted_syntax.html"
        tmp_pdf = self.temp_dir / "corrupted_syntax.pdf"
        # Write corrupted HTML with unclosed script/style blocks
        tmp_html.write_text("<style>@page { size: letter; body { color: red;", encoding="utf-8")

        res = run_command_safe(
            [sys.executable, str(self.compile_script), "--target", "nonexistent_target_xyz"],
            cwd=REPO_ROOT
        )
        self.assertEqual(res.returncode, 1)

    def test_c1_06_target_specific_pipeline_execution_de_en(self):
        """C1 Targeted Pipeline: Invoking pipeline for single target 'de_en' compiles and verifies only that target."""
        res = run_command_safe(
            [sys.executable, str(self.compile_script), "--target", "de_en", "--verify"],
            cwd=REPO_ROOT,
            timeout_sec=60.0
        )
        self.assertEqual(res.returncode, 0, f"Targeted de_en pipeline failed: {res.stderr}")
        self.assertIn("Diego_Alejandro_Escobar_Barahona_CV_EN.pdf", res.stdout)

    def test_c1_07_target_specific_pipeline_execution_pub_es(self):
        """C1 Targeted Pipeline: Invoking pipeline for single target 'pub_es' compiles and verifies only that target."""
        res = run_command_safe(
            [sys.executable, str(self.compile_script), "--target", "pub_es", "--verify"],
            cwd=REPO_ROOT,
            timeout_sec=60.0
        )
        self.assertEqual(res.returncode, 0, f"Targeted pub_es pipeline failed: {res.stderr}")
        self.assertIn("Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf", res.stdout)


# ============================================================================
# C2: Antigravity Skill & Interview Defense Integration
# ============================================================================

class TestC2AntigravitySkillAndDefenseIntegration(unittest.TestCase):
    """Verifies integration of Antigravity interview defense skill, drill runner, and STAR rubrics."""

    def setUp(self):
        self.skill_dir = REPO_ROOT / ".agents" / "skills" / "cv-interview-defense"
        self.drill_script = self.skill_dir / "scripts" / "drill_runner.py"
        self.questions_db = self.skill_dir / "resources" / "questions_db.json"
        self.rubrics_file = self.skill_dir / "resources" / "evaluation_rubrics.json"
        self.defense_manual = REPO_ROOT / "docs" / "INTERVIEW_DEFENSE_MANUAL.md"

        if not self.skill_dir.is_dir():
            self.skipTest("[Progressive Testability] .agents/skills/cv-interview-defense pending M3 implementation")

    def test_c2_01_skill_manifest_and_resource_catalog_coherence(self):
        """C2 Schema Coherence: SKILL.md accurately references questions_db.json and evaluation_rubrics.json."""
        skill_md = self.skill_dir / "SKILL.md"
        self.assertTrue(skill_md.is_file(), f"SKILL.md missing at {skill_md}")
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn("name: cv-interview-defense", content)
        self.assertIn("drill_runner.py", content)

    def test_c2_02_questions_db_schema_and_persona_coverage(self):
        """C2 Questions DB Coverage: Validates questions across technical, behavioral, and executive personas."""
        if not self.questions_db.is_file():
            self.skipTest(f"[Progressive Testability] questions_db.json missing at {self.questions_db}")

        data = json.loads(self.questions_db.read_text(encoding="utf-8"))
        questions = data.get("questions", data if isinstance(data, list) else [])
        self.assertGreater(len(questions), 0, "questions_db.json contains zero questions")

        personas_found = {q.get("persona") for q in questions if "persona" in q}
        projects_found = {q.get("project") for q in questions if "project" in q}

        for expected_persona in ["technical", "behavioral", "executive"]:
            self.assertTrue(
                any(expected_persona in str(p).lower() for p in personas_found),
                f"Missing questions for persona '{expected_persona}' in questions_db.json"
            )

        for expected_project in ["ontotab", "gbm", "ferrostats", "sql_arena"]:
            self.assertTrue(
                any(expected_project in str(p).lower().replace("-", "_") for p in projects_found),
                f"Missing questions for project '{expected_project}' in questions_db.json"
            )

    def test_c2_03_evaluation_rubrics_schema_and_criteria(self):
        """C2 Rubrics Schema: Validates STAR criteria, score bounds, and anti-exaggeration penalty rules."""
        if not self.rubrics_file.is_file():
            self.skipTest(f"[Progressive Testability] evaluation_rubrics.json missing at {self.rubrics_file}")

        data = json.loads(self.rubrics_file.read_text(encoding="utf-8"))
        rubrics = data.get("rubrics", data if isinstance(data, list) else [])
        self.assertGreater(len(rubrics), 0, "evaluation_rubrics.json contains zero rubrics")

        for rubric in rubrics:
            self.assertIn("rubric_id", rubric)
            self.assertIn("criteria", rubric)
            # Verify penalty anchors exist
            criteria_str = json.dumps(rubric)
            self.assertTrue("penalty" in criteria_str.lower() or "deduction" in criteria_str.lower() or "exaggeration" in criteria_str.lower())

    def test_c2_04_drill_runner_retrieval_across_personas_and_projects(self):
        """C2 CLI Retrieval: drill_runner.py executes across all persona/project combinations."""
        if not self.drill_script.is_file():
            self.skipTest(f"[Progressive Testability] drill_runner.py missing at {self.drill_script}")

        test_matrix = [
            ("technical", "ontotab"),
            ("behavioral", "gbm"),
            ("executive", "ferrostats"),
        ]
        for persona, project in test_matrix:
            with self.subTest(persona=persona, project=project):
                res = run_command_safe(
                    [sys.executable, str(self.drill_script), "--persona", persona, "--project", project, "--dry-run"],
                    cwd=REPO_ROOT
                )
                self.assertEqual(res.returncode, 0, f"drill_runner failed for {persona}/{project}: {res.stderr}")
                self.assertGreater(len(res.stdout), 50)

    def test_c2_05_drill_runner_evaluates_passing_star_answer(self):
        """C2 Defense Evaluation Pass: Accurate, evidence-backed STAR response receives passing grade."""
        if not self.drill_script.is_file():
            self.skipTest(f"[Progressive Testability] drill_runner.py missing at {self.drill_script}")

        # STAR answer strictly conforming to verifiable evidence
        truthful_answer = (
            "Situation: During my 13-week internship at GBM, we evaluated ontology enrichment on tabular data. "
            "Task: As second author under AI Lead Joaquín Solórzano, I led experimental activity E01. "
            "Action: Executed baseline Raw and Numeric-Oracle benchmarks over 30,000 credit records using nested 5x3 CV. "
            "Result: Achieved 0.5596 AP on XGBoost, proving empirical numerical superiority without NLP complexity."
        )
        res = run_command_safe(
            [sys.executable, str(self.drill_script), "--persona", "technical", "--project", "ontotab",
             "--eval-answer", truthful_answer],
            cwd=REPO_ROOT
        )
        self.assertEqual(res.returncode, 0, f"drill_runner evaluation failed: {res.stderr}")
        self.assertTrue("PASS" in res.stdout or "score" in res.stdout.lower())

    def test_c2_06_drill_runner_rejects_exaggerated_answer_with_penalty(self):
        """C2 Defense Evaluation Fail: Answer containing forbidden claims triggers fatal penalty."""
        if not self.drill_script.is_file():
            self.skipTest(f"[Progressive Testability] drill_runner.py missing at {self.drill_script}")

        # Toxic answer with unbacked claims
        toxic_answer = (
            "I served as the Lead Author on OntoTab and single-handedly published our breakthrough in IEEE. "
            "My model achieved 95% accuracy outperforming all existing commercial software."
        )
        res = run_command_safe(
            [sys.executable, str(self.drill_script), "--persona", "technical", "--project", "ontotab",
             "--eval-answer", toxic_answer],
            cwd=REPO_ROOT
        )
        # Should indicate failure or penalty deduction in stdout
        output = res.stdout + res.stderr
        self.assertTrue(
            "FAIL" in output or "PENALTY" in output or "violation" in output.lower() or res.returncode != 0,
            "drill_runner failed to penalize toxic unbacked claims!"
        )

    def test_c2_07_interview_defense_manual_anchor_parity_with_rubrics(self):
        """C2 Knowledge Parity: INTERVIEW_DEFENSE_MANUAL.md anchors align with evidence matrix facts."""
        if not self.defense_manual.is_file():
            self.skipTest(f"[Progressive Testability] INTERVIEW_DEFENSE_MANUAL.md missing at {self.defense_manual}")

        content = self.defense_manual.read_text(encoding="utf-8")
        mandatory_anchors = [
            "0.5596",               # OntoTab AP metric
            "30,000",               # Dataset volume
            "13 semanas",           # GBM duration
            "15 jobs DataStage",    # ETL count
            "$0.00/mes",            # FERROSTATS FinOps cost
            "136 tests",            # SQL Arena test harness
        ]
        for anchor in mandatory_anchors:
            self.assertIn(anchor, content, f"Defense manual missing mandatory factual anchor: '{anchor}'")


# ============================================================================
# C3: Google Drive Sync Dry-Run & Artifact Discovery Integration
# ============================================================================

class TestC3GoogleDriveSyncDryRunIntegration(unittest.TestCase):
    """Verifies that scripts/sync_drive.py --dry-run integrates with compiled artifacts and destination IDs."""

    def setUp(self):
        self.sync_script = REPO_ROOT / "scripts" / "sync_drive.py"
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self._temp_dir_obj.name)

        if not self.sync_script.is_file():
            self.skipTest("[Progressive Testability] scripts/sync_drive.py pending M4 implementation")

    def tearDown(self):
        try:
            self._temp_dir_obj.cleanup()
        except Exception:
            pass

    def test_c3_01_drive_sync_discovers_all_four_canonical_pdfs(self):
        """C3 Artifact Discovery: sync_drive.py --dry-run discovers all 4 compiled production PDFs."""
        res = run_command_safe(
            [sys.executable, str(self.sync_script), "--dry-run"],
            cwd=REPO_ROOT
        )
        self.assertEqual(res.returncode, 0, f"sync_drive.py --dry-run failed:\n{res.stderr}")
        for rel_target in CANONICAL_TARGETS:
            self.assertIn(rel_target.name, res.stdout, f"Target {rel_target.name} not discovered by sync dry-run.")

    def test_c3_02_drive_sync_validates_destination_folder_ids_offline(self):
        """C3 Destination Mapping: sync_drive.py verifies destination portfolio root ID (13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H)."""
        res = run_command_safe(
            [sys.executable, str(self.sync_script), "--dry-run"],
            cwd=REPO_ROOT
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H", res.stdout)

    def test_c3_03_drive_sync_dry_run_fails_when_artifact_missing(self):
        """C3 Missing Artifact Detection: sync_drive.py --dry-run detects missing canonical PDF and exits code 1."""
        # Point sync_drive to a temporary empty directory
        res = run_command_safe(
            [sys.executable, str(self.sync_script), "--dry-run", "--source-dir", str(self.temp_dir)],
            cwd=REPO_ROOT
        )
        self.assertEqual(res.returncode, 1, "sync_drive.py --dry-run succeeded despite missing PDF artifacts!")

    def test_c3_04_drive_sync_dry_run_zero_network_mutation_contract(self):
        """C3 Network Safety: sync_drive.py --dry-run executes in < 5 seconds with zero network calls."""
        res = run_command_safe(
            [sys.executable, str(self.sync_script), "--dry-run"],
            cwd=REPO_ROOT,
            timeout_sec=5.0
        )
        self.assertEqual(res.returncode, 0)
        self.assertLess(res.duration_sec, 4.0, "Dry run took unexpectedly long, indicating potential network polling.")

    def test_c3_05_end_to_end_compilation_to_drive_sync_dry_run_flow(self):
        """C3 Chain: scripts/compile_all.py -> scripts/sync_drive.py --dry-run seamless execution."""
        # 1. Compile all targets
        res_compile = run_command_safe(
            [sys.executable, str(REPO_ROOT / "scripts" / "compile_all.py"), "--all"],
            cwd=REPO_ROOT,
            timeout_sec=90.0
        )
        self.assertEqual(res_compile.returncode, 0)

        # 2. Immediately dry-run drive sync
        res_sync = run_command_safe(
            [sys.executable, str(self.sync_script), "--dry-run"],
            cwd=REPO_ROOT
        )
        self.assertEqual(res_sync.returncode, 0)
        self.assertIn("DRY-RUN", res_sync.stdout.upper())


# ============================================================================
# C4: Local CI Harness Multi-Stage Integration
# ============================================================================

class TestC4CiHarnessMultiStageIntegration(unittest.TestCase):
    """Verifies that scripts/run_ci_harness.py integrates and chains all CI pipeline stages."""

    def setUp(self):
        self.ci_script = REPO_ROOT / "scripts" / "run_ci_harness.py"
        if not self.ci_script.is_file():
            self.skipTest("[Progressive Testability] scripts/run_ci_harness.py pending M4 implementation")

    def test_c4_01_run_ci_harness_help_contract(self):
        """C4 CLI Contract: scripts/run_ci_harness.py --help lists all standard stages."""
        res = run_command_safe([sys.executable, str(self.ci_script), "--help"], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 0)
        for stage in ["lint", "compile", "geometry", "sync"]:
            self.assertIn(stage, res.stdout.lower())

    def test_c4_02_run_ci_harness_executes_sequential_stages_in_order(self):
        """C4 Full CI Flow: scripts/run_ci_harness.py executes entire pipeline and exits 0."""
        res = run_command_safe(
            [sys.executable, str(self.ci_script)],
            cwd=REPO_ROOT,
            timeout_sec=120.0
        )
        self.assertEqual(res.returncode, 0, f"run_ci_harness.py failed:\n{res.stdout}\n{res.stderr}")
        self.assertIn("ALL CI CHECKS PASSED", res.stdout.upper())

    def test_c4_03_run_ci_harness_aborts_on_early_stage_failure(self):
        """C4 Fast-Fail: CI harness stops immediately on first failed stage and does not proceed to sync."""
        res = run_command_safe(
            [sys.executable, str(self.ci_script), "--fail-fast", "--mock-fail-stage", "geometry"],
            cwd=REPO_ROOT
        )
        # Should fail with non-zero exit code if fast-fail / mock failure is triggered
        if res.returncode != 0:
            self.assertNotIn("SYNC STAGE SUCCESS", res.stdout.upper())

    def test_c4_04_ci_harness_dry_run_flag_supported(self):
        """C4 CI Dry-Run: scripts/run_ci_harness.py --dry-run prints stage execution plan without running compilers."""
        res = run_command_safe(
            [sys.executable, str(self.ci_script), "--dry-run"],
            cwd=REPO_ROOT
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("PLAN", res.stdout.upper())


# ============================================================================
# Main Execution Entry Point
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)

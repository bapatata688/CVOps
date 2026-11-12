#!/usr/bin/env python3
"""test_adversarial_m4.py - Adversarial Stress & Cascade Verification for Milestone 4

Rigorously verifies:
1. scripts/sync_drive.py:
   - Empty directory discovery failure (--dry-run --source-dir <empty_dir>) exits 1.
   - Normal dry-run performance (< 5s), exact ID mappings, canonical discoveries, and exit 0.
   - CLI boundary defenses (invalid options, missing arguments, non-existent directories, 0-byte PDFs).
   - Artifact discovery robustness (flat directory structure vs nested canonical structure).
2. scripts/run_ci_harness.py:
   - Fast-fail mechanics for all 4 mock-fail stages (--mock-fail-stage {lint,compile,geometry,sync}).
   - Verification that any stage failure immediately aborts and marks subsequent stages as SKIPPED.
   - Dry-run execution plan output containing "PLAN" and exit code 0.
   - CLI boundary defenses (unrecognized options, invalid mock stage choices).
   - Clean execution happy path passing all 4 stages with exit code 0.
3. Interaction and cascade isolation:
   - Injecting ethical violations or missing templates into CV sources.
   - Asserting that CI runner aborts immediately at stage 1 (lint) without ever executing compile, geometry, or sync.

Compliance:
- Zero Pytest / Zero Matplotlib (AGENTS.md Rule 5 compliant).
- Python standard library unittest only.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
CV_DIR = REPO_ROOT / "cv"

SYNC_DRIVE_SCRIPT = SCRIPTS_DIR / "sync_drive.py"
RUN_CI_SCRIPT = SCRIPTS_DIR / "run_ci_harness.py"
LINT_SCRIPT = SCRIPTS_DIR / "lint_cv_truth.py"

PORTFOLIO_ROOT_ID = "13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H"
CV_PREP_FOLDER_ID = "17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb"
MASTER_PROFILE_DOC_ID = "16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ"

CANONICAL_PDF_NAMES = [
    "Diego_Alejandro_Escobar_Barahona_CV_EN.pdf",
    "Diego_Alejandro_Escobar_Barahona_CV_ES.pdf",
    "Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf",
    "Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf",
]


class TestSyncDriveAdversarial(unittest.TestCase):
    """Adversarial and boundary test harness for scripts/sync_drive.py."""

    def test_empty_source_dir_fails_fast_and_exits_1(self):
        """Asserts that pointing --source-dir to an empty directory detects missing PDFs and exits 1."""
        with tempfile.TemporaryDirectory() as empty_tmp:
            cmd = [
                sys.executable,
                str(SYNC_DRIVE_SCRIPT),
                "--dry-run",
                "--source-dir",
                empty_tmp,
            ]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1, f"Expected exit code 1, got {proc.returncode}")
            self.assertIn("ARTIFACT DISCOVERY ERRORS", proc.stderr)
            for pdf_name in CANONICAL_PDF_NAMES:
                self.assertIn(pdf_name, proc.stderr)
            self.assertIn("Discovered only 0 of 4 canonical PDFs", proc.stderr)

    def test_dry_run_happy_path_performance_and_metadata(self):
        """Asserts --dry-run completes in < 5 seconds, contains 'DRY-RUN', verifies IDs, and exits 0."""
        start_time = time.perf_counter()
        cmd = [sys.executable, str(SYNC_DRIVE_SCRIPT), "--dry-run"]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        elapsed = time.perf_counter() - start_time

        self.assertEqual(proc.returncode, 0, f"Expected exit code 0, got {proc.returncode}. Stderr: {proc.stderr}")
        self.assertLess(elapsed, 5.0, f"Execution took {elapsed:.2f}s, exceeding 5.0s budget")
        self.assertIn("DRY-RUN", proc.stdout)
        self.assertIn(PORTFOLIO_ROOT_ID, proc.stdout)
        self.assertIn(CV_PREP_FOLDER_ID, proc.stdout)
        self.assertIn(MASTER_PROFILE_DOC_ID, proc.stdout)

        for pdf_name in CANONICAL_PDF_NAMES:
            self.assertIn(pdf_name, proc.stdout)
        self.assertIn("SUCCESS: Offline sync validation completed successfully", proc.stdout)

    def test_invalid_cli_arguments_rejected(self):
        """Asserts invalid CLI flags cause immediate rejection with exit code 2."""
        invalid_flag_sets = [
            ["--unrecognized-option"],
            ["--bogus-flag"],
            ["--source-dir"],  # Missing argument value
            ["-z"],
        ]
        for flags in invalid_flag_sets:
            cmd = [sys.executable, str(SYNC_DRIVE_SCRIPT)] + flags
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(
                proc.returncode,
                2,
                f"Expected exit code 2 for invalid flags {flags}, got {proc.returncode}"
            )
            self.assertTrue(
                "usage:" in proc.stderr.lower() or "error:" in proc.stderr.lower(),
                f"Expected clean error/usage output for flags {flags}"
            )

    def test_non_existent_source_directory_fails(self):
        """Asserts that a non-existent source directory cleanly exits with code 1."""
        bogus_dir = REPO_ROOT / "non_existent_dir_adversarial_test_999"
        cmd = [
            sys.executable,
            str(SYNC_DRIVE_SCRIPT),
            "--dry-run",
            "--source-dir",
            str(bogus_dir),
        ]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Source directory does not exist", proc.stderr)

    def test_zero_byte_pdf_detected_and_rejected(self):
        """Asserts that 0-byte canonical PDFs are caught and rejected with exit code 1."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Create a 0-byte PDF matching a canonical name
            zero_byte_pdf = tmp_path / "Diego_Alejandro_Escobar_Barahona_CV_EN.pdf"
            zero_byte_pdf.touch()

            cmd = [
                sys.executable,
                str(SYNC_DRIVE_SCRIPT),
                "--dry-run",
                "--source-dir",
                tmp_dir,
            ]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("is 0 bytes", proc.stderr)

    def test_flat_directory_fallback_discovery(self):
        """Asserts that canonical PDFs stored in a flat root folder are successfully discovered."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Copy all 4 PDFs to flat root
            shutil.copy(CV_DIR / "01_produccion_data_engineering" / "en" / CANONICAL_PDF_NAMES[0], tmp_path)
            shutil.copy(CV_DIR / "01_produccion_data_engineering" / "es" / CANONICAL_PDF_NAMES[1], tmp_path)
            shutil.copy(CV_DIR / "02_publicacion_ia_investigacion" / "en" / CANONICAL_PDF_NAMES[2], tmp_path)
            shutil.copy(CV_DIR / "02_publicacion_ia_investigacion" / "es" / CANONICAL_PDF_NAMES[3], tmp_path)

            cmd = [
                sys.executable,
                str(SYNC_DRIVE_SCRIPT),
                "--dry-run",
                "--source-dir",
                tmp_dir,
            ]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("All 4 canonical PDF artifacts discovered", proc.stdout)

    def test_partial_artifacts_detected(self):
        """Asserts that having only 3 of 4 canonical PDFs is rejected with exit code 1."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Copy only 3 PDFs
            shutil.copy(CV_DIR / "01_produccion_data_engineering" / "en" / CANONICAL_PDF_NAMES[0], tmp_path)
            shutil.copy(CV_DIR / "01_produccion_data_engineering" / "es" / CANONICAL_PDF_NAMES[1], tmp_path)
            shutil.copy(CV_DIR / "02_publicacion_ia_investigacion" / "en" / CANONICAL_PDF_NAMES[2], tmp_path)

            cmd = [
                sys.executable,
                str(SYNC_DRIVE_SCRIPT),
                "--dry-run",
                "--source-dir",
                tmp_dir,
            ]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("Discovered only 3 of 4 canonical PDFs", proc.stderr)


class TestRunCiHarnessAdversarial(unittest.TestCase):
    """Adversarial and fast-fail test harness for scripts/run_ci_harness.py."""

    def test_mock_fail_stage_lint_aborts_immediately(self):
        """Asserts mock failure at lint stage halts pipeline immediately, skipping compile, geometry, sync."""
        cmd = [sys.executable, str(RUN_CI_SCRIPT), "--mock-fail-stage", "lint"]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("[STAGE: lint    ] : FAIL", proc.stdout)
        self.assertIn("[STAGE: compile ] : SKIPPED (due to early abort)", proc.stdout)
        self.assertIn("[STAGE: geometry] : SKIPPED (due to early abort)", proc.stdout)
        self.assertIn("[STAGE: sync    ] : SKIPPED (due to early abort)", proc.stdout)
        self.assertIn("[FAST-FAIL] Aborting subsequent stages immediately.", proc.stderr)
        self.assertIn("VERDICT: [FAIL]", proc.stderr)

    def test_mock_fail_stage_compile_aborts_immediately(self):
        """Asserts mock failure at compile stage halts pipeline, skipping geometry and sync."""
        cmd = [sys.executable, str(RUN_CI_SCRIPT), "--mock-fail-stage", "compile"]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("[STAGE: lint    ] : PASS", proc.stdout)
        self.assertIn("[STAGE: compile ] : FAIL", proc.stdout)
        self.assertIn("[STAGE: geometry] : SKIPPED (due to early abort)", proc.stdout)
        self.assertIn("[STAGE: sync    ] : SKIPPED (due to early abort)", proc.stdout)
        self.assertIn("[FAST-FAIL] Aborting subsequent stages immediately.", proc.stderr)
        self.assertIn("VERDICT: [FAIL]", proc.stderr)

    def test_mock_fail_stage_geometry_aborts_immediately(self):
        """Asserts mock failure at geometry stage halts pipeline, skipping sync."""
        cmd = [sys.executable, str(RUN_CI_SCRIPT), "--mock-fail-stage", "geometry"]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("[STAGE: lint    ] : PASS", proc.stdout)
        self.assertIn("[STAGE: compile ] : PASS", proc.stdout)
        self.assertIn("[STAGE: geometry] : FAIL", proc.stdout)
        self.assertIn("[STAGE: sync    ] : SKIPPED (due to early abort)", proc.stdout)
        self.assertIn("[FAST-FAIL] Aborting subsequent stages immediately.", proc.stderr)
        self.assertIn("VERDICT: [FAIL]", proc.stderr)

    def test_mock_fail_stage_sync_fails_overall(self):
        """Asserts mock failure at sync stage fails overall CI execution."""
        cmd = [sys.executable, str(RUN_CI_SCRIPT), "--mock-fail-stage", "sync"]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("[STAGE: lint    ] : PASS", proc.stdout)
        self.assertIn("[STAGE: compile ] : PASS", proc.stdout)
        self.assertIn("[STAGE: geometry] : PASS", proc.stdout)
        self.assertIn("[STAGE: sync    ] : FAIL", proc.stdout)
        self.assertIn("VERDICT: [FAIL]", proc.stderr)

    def test_dry_run_execution_plan(self):
        """Asserts --dry-run outputs execution PLAN with all 4 stages and exits 0."""
        cmd = [sys.executable, str(RUN_CI_SCRIPT), "--dry-run"]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("PLAN", proc.stdout)
        self.assertIn("lint", proc.stdout)
        self.assertIn("compile", proc.stdout)
        self.assertIn("geometry", proc.stdout)
        self.assertIn("sync", proc.stdout)
        self.assertIn("dry-run complete", proc.stdout.lower())

    def test_invalid_cli_arguments_rejected(self):
        """Asserts invalid CLI flags cause immediate rejection with exit code 2."""
        invalid_flag_sets = [
            ["--invalid-arg"],
            ["--bogus"],
            ["--mock-fail-stage", "invalid_stage_name"],
        ]
        for flags in invalid_flag_sets:
            cmd = [sys.executable, str(RUN_CI_SCRIPT)] + flags
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(
                proc.returncode,
                2,
                f"Expected exit code 2 for invalid flags {flags}, got {proc.returncode}"
            )
            self.assertIn("error:", proc.stderr.lower())

    def test_clean_ci_harness_pass(self):
        """Asserts clean execution runs all 4 stages, outputs 'ALL CI CHECKS PASSED', and exits 0."""
        cmd = [sys.executable, str(RUN_CI_SCRIPT)]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Expected 0, got {proc.returncode}. Stderr: {proc.stderr}")
        self.assertIn("[STAGE: lint    ] : PASS", proc.stdout)
        self.assertIn("[STAGE: compile ] : PASS", proc.stdout)
        self.assertIn("[STAGE: geometry] : PASS", proc.stdout)
        self.assertIn("[STAGE: sync    ] : PASS", proc.stdout)
        self.assertIn("ALL CI CHECKS PASSED", proc.stdout)
        self.assertIn("VERDICT: [PASS]", proc.stdout)


class TestCascadeAndIsolationInteraction(unittest.TestCase):
    """Verifies that actual source corruptions halt the pipeline before reaching sync."""

    def test_ethical_violation_in_template_aborts_ci_before_sync(self):
        """Injecting a forbidden seniority claim into an HTML template halts CI at lint and never touches sync."""
        target_template = CV_DIR / "01_produccion_data_engineering" / "en" / "Diego_Alejandro_Escobar_Barahona_CV_EN.html"
        original_text = target_template.read_text(encoding="utf-8")

        try:
            # Corrupt template by injecting forbidden title
            corrupted_text = original_text.replace("Junior Data Engineer", "Senior Data Engineer")
            self.assertNotEqual(original_text, corrupted_text)
            target_template.write_text(corrupted_text, encoding="utf-8")

            cmd = [sys.executable, str(RUN_CI_SCRIPT)]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)

            self.assertEqual(proc.returncode, 1)
            self.assertIn("[STAGE: lint    ] : FAIL", proc.stdout)
            self.assertIn("[STAGE: compile ] : SKIPPED (due to early abort)", proc.stdout)
            self.assertIn("[STAGE: geometry] : SKIPPED (due to early abort)", proc.stdout)
            self.assertIn("[STAGE: sync    ] : SKIPPED (due to early abort)", proc.stdout)
            self.assertIn("[FAST-FAIL] Aborting subsequent stages immediately.", proc.stderr)
            self.assertIn("Senior Data Engineer", proc.stdout)
        finally:
            # Cleanly restore template
            target_template.write_text(original_text, encoding="utf-8")

        # Verify restoration was clean
        self.assertEqual(target_template.read_text(encoding="utf-8"), original_text)

    def test_missing_template_aborts_ci_before_sync(self):
        """Moving an HTML template away causes linter to fail and halts pipeline before compile or sync."""
        target_template = CV_DIR / "01_produccion_data_engineering" / "en" / "Diego_Alejandro_Escobar_Barahona_CV_EN.html"
        backup_template = target_template.with_suffix(".html.adversarial_bak")

        target_template.rename(backup_template)
        try:
            cmd = [sys.executable, str(RUN_CI_SCRIPT)]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)

            self.assertEqual(proc.returncode, 1)
            self.assertIn("[STAGE: lint    ] : FAIL", proc.stdout)
            self.assertIn("[STAGE: compile ] : SKIPPED (due to early abort)", proc.stdout)
            self.assertIn("[STAGE: geometry] : SKIPPED (due to early abort)", proc.stdout)
            self.assertIn("[STAGE: sync    ] : SKIPPED (due to early abort)", proc.stdout)
            self.assertIn("[FAST-FAIL] Aborting subsequent stages immediately.", proc.stderr)
            self.assertIn("Target file does not exist", proc.stderr)
        finally:
            if backup_template.exists():
                backup_template.rename(target_template)

        self.assertTrue(target_template.is_file())


if __name__ == "__main__":
    unittest.main()

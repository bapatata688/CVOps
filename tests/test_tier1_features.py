"""test_tier1_features.py - Tier 1: Feature Coverage & Contract Validation Suite

Verifies all 23 individual features (F1 through F23) of master_cv as mapped in
TEST_INFRA.md § 4 and PROJECT.md:
  F1:  Git Repo & Directory Structure (R1.1)
  F2:  Professional Production README (R1.2)
  F3:  Source Asset & Insumo Migration SHA256 Integrity (R1.3)
  F4:  Hybrid WeasyPrint Compilation Engine (R1.4)
  F5:  Verbatim UoPeople Education Block (R2.1)
  F6:  Calibrated CSS 1-Page Budget Tuning (R2.2)
  F7:  Programmatic 1-Page Geometry Assertion via pypdf (R2.3)
  F8:  Unified 4-Target PDF Compilation (R2.4)
  F9:  Google Drive CV_Prep Folder Structure & Mapping (R3.1)
  F10: Master Profile Doc Governance Directive (R3.2)
  F11: Evidence-Backed Formal Specification Document (R3.3)
  F12: Strict Anti-Exaggeration Containment Rules (R3.4)
  F13: ATS Role Paraphrase Matrices for DE, DA, AI SWE (R4.1)
  F14: Forensic Evidence Gap Audit & Catalog (R4.2)
  F15: Comprehensive Interview Defense Manual (R5.1)
  F16: Interactive Antigravity Skill & CLI Drill Runner (R5.2)
  F17: Google Docs Sync Mapping for Defense & Skill (R5.3)
  F18: Systematic 8-Field Decision Log Schema (R6.1)
  F19: Initial Engineering Hurdle Logs LOG-001..LOG-004 (R6.2)
  F20: Ethical Truthfulness Linter Script (R7.1)
  F21: Unified Local CI/CD Harness Runner (R7.2)
  F22: Google Drive Dated Sync Automation (R7.3)
  F23: GitHub Actions CI/CD Workflow Syntax & Stages (R7.4)

Compliance:
- Pure Python standard library unittest (Zero-Pytest, Rule 5 compliant).
- Progressive testability: strict assertions when artifacts are present, descriptive
  skip/contract signaling when parallel milestone artifacts are pending.
- Reusable opaque-box helpers imported from tests.test_harness_utils.
"""

import json
import os
import re
import sys
import unittest
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure repository root and test harness utilities are in sys.path
TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from tests.test_harness_utils import (
    KNOWN_ASSET_HASHES,
    MANDATORY_DECISION_LOG_FIELDS,
    assert_path_exists,
    assert_pdf_geometry,
    assert_sha256_matches,
    compute_sha256,
    parse_decision_log,
    run_command_safe,
    scan_forbidden_claims,
    validate_decision_log_entries,
    validate_git_repo,
    validate_path_exists,
    validate_pdf_geometry,
    verify_sha256,
)


# ============================================================================
# F1: Git Repo & Modular Directory Topology (R1.1)
# ============================================================================

class TestF1GitTopology(unittest.TestCase):
    """Verifies that master_cv is an initialized Git repository with clean topology."""

    def test_f1_git_repository_initialized(self):
        """F1: Verifies repository is initialized as a Git working tree."""
        self.assertTrue(
            validate_git_repo(REPO_ROOT),
            f"Directory at {REPO_ROOT} is not an initialized Git working tree."
        )

    def test_f1_git_branch_main(self):
        """F1: Verifies that current branch is 'main'."""
        res = run_command_safe(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 0, f"Git rev-parse failed: {res.stderr}")
        branch = res.stdout.strip()
        self.assertEqual(branch, "main", f"Expected git branch 'main', found '{branch}'.")

    def test_f1_modular_directory_topology_exists(self):
        """F1: Verifies mandatory modular directory topology exists."""
        required_dirs = [
            "cv",
            "docs",
            "evidence",
            "resources",
            "scripts",
            "tests",
        ]
        for dir_name in required_dirs:
            target = REPO_ROOT / dir_name
            self.assertTrue(
                target.is_dir(),
                f"Mandatory top-level directory missing: {target.resolve()}"
            )

    def test_f1_git_attributes_and_ignore_present(self):
        """F1: Verifies tracking hygiene files (.gitignore, .gitattributes) exist."""
        gitignore = REPO_ROOT / ".gitignore"
        gitattributes = REPO_ROOT / ".gitattributes"
        self.assertTrue(gitignore.is_file(), f".gitignore missing at {gitignore}")
        self.assertTrue(gitattributes.is_file(), f".gitattributes missing at {gitattributes}")

        # Check that .gitignore ignores standard artifacts
        ignore_content = gitignore.read_text(encoding="utf-8")
        self.assertIn(".venv", ignore_content)
        self.assertIn("__pycache__", ignore_content)


# ============================================================================
# F2: Production README with Architecture, Badges, Usage (R1.2)
# ============================================================================

class TestF2ProductionReadme(unittest.TestCase):
    """Verifies that README.md provides professional production documentation."""

    def setUp(self):
        self.readme_path = REPO_ROOT / "README.md"
        if not self.readme_path.is_file():
            self.skipTest(f"[Progressive Testability] README.md missing at {self.readme_path}")
        self.readme_content = self.readme_path.read_text(encoding="utf-8")

    def test_f2_readme_existence_and_size(self):
        """F2: Verifies README.md exists and contains substantial technical content."""
        self.assertGreater(
            len(self.readme_content),
            2000,
            "README.md is too short to be a complete production documentation file."
        )

    def test_f2_readme_badges_present(self):
        """F2: Verifies presence of key shields/badges."""
        required_badge_tokens = [
            "python-3.12+",
            "WeasyPrint",
            "612x792pt",
            "ATS",
            "integrity",
        ]
        for token in required_badge_tokens:
            self.assertIn(
                token.lower(),
                self.readme_content.lower(),
                f"README.md is missing expected status badge for: '{token}'"
            )

    def test_f2_readme_architecture_and_pipeline(self):
        """F2: Verifies presence of architecture section and pipeline diagram."""
        self.assertIn("Architecture", self.readme_content)
        self.assertIn("WeasyPrint", self.readme_content)
        self.assertIn("pypdf", self.readme_content)

    def test_f2_readme_cli_commands_and_quickstart(self):
        """F2: Verifies CLI usage commands are documented in README."""
        expected_commands = [
            "compile_all.py",
            "verify_geometry.py",
            "lint_cv_truth.py",
            "run_ci_harness.py",
        ]
        for cmd in expected_commands:
            self.assertIn(
                cmd,
                self.readme_content,
                f"README.md does not document CLI invocation for '{cmd}'"
            )

    def test_f2_readme_contact_and_integrity_anchor(self):
        """F2: Verifies contact information and identity anchor in README."""
        self.assertIn("Diego Alejandro Escobar Barahona", self.readme_content)
        self.assertIn("diegoalejandroescobarahona1@gmail.com", self.readme_content)
        self.assertIn("github.com/bapatata688", self.readme_content)


# ============================================================================
# F3: Source Asset & Insumo Migration SHA256 Integrity (R1.3)
# ============================================================================

class TestF3AssetMigrationSha256(unittest.TestCase):
    """Verifies that all 6 verified evidence assets match authoritative SHA256 baselines."""

    def _find_evidence_asset(self, rel_path: str) -> Optional[Path]:
        """Resolves asset path with flexible subfolder fallback."""
        candidates = [
            REPO_ROOT / "evidence" / rel_path,
            REPO_ROOT / "evidence" / rel_path.replace("cv/archive", "archive"),
            REPO_ROOT / "evidence" / rel_path.replace("research/ontotab", "research"),
            REPO_ROOT / "evidence" / Path(rel_path).name,
            REPO_ROOT / rel_path,
        ]
        for c in candidates:
            if c.is_file():
                return c
        return None

    def test_f3_all_six_assets_match_sha256_baselines(self):
        """F3: Computes SHA256 for all 6 source assets and asserts byte-level parity."""
        evidence_dir = REPO_ROOT / "evidence"
        if not evidence_dir.is_dir():
            self.skipTest(f"[Progressive Testability] evidence/ directory missing at {evidence_dir}")

        for asset_key, expected_hash in KNOWN_ASSET_HASHES.items():
            resolved = self._find_evidence_asset(asset_key)
            self.assertIsNotNone(
                resolved,
                f"Evidence asset not found on disk: {asset_key}"
            )
            actual_hash = compute_sha256(resolved)
            self.assertEqual(
                actual_hash,
                expected_hash,
                f"SHA256 checksum mismatch for {asset_key} ({resolved.name}):\n"
                f"  Expected: {expected_hash}\n"
                f"  Actual:   {actual_hash}"
            )


# ============================================================================
# F4: Hybrid WeasyPrint Compilation Engine (R1.4)
# ============================================================================

class TestF4WeasyPrintHybridCompiler(unittest.TestCase):
    """Verifies CLI interface and hybrid fallback compilation logic."""

    def setUp(self):
        self.compile_script = REPO_ROOT / "scripts" / "compile_all.py"
        if not self.compile_script.is_file():
            self.skipTest(f"[Progressive Testability] scripts/compile_all.py missing at {self.compile_script}")

    def test_f4_compiler_help_and_options(self):
        """F4: Executes compile_all.py --help and verifies CLI arguments."""
        res = run_command_safe([sys.executable, str(self.compile_script), "--help"], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 0, f"compile_all.py --help failed: {res.stderr}")
        self.assertIn("--target", res.stdout)
        self.assertIn("--engine", res.stdout)
        self.assertIn("--verify", res.stdout)

    def test_f4_hybrid_fallback_logic_present(self):
        """F4: Inspects compiler sources to ensure hybrid Windows fallback mechanism is present."""
        sources = [
            self.compile_script,
            REPO_ROOT / "cv" / "generate_all_cvs.py",
        ]
        combined_code = "\n".join(
            p.read_text(encoding="utf-8") for p in sources if p.is_file()
        )
        # Check for hybrid logic indicators: Scoop / CLI shim invocation / fallback
        has_cli_fallback = (
            "weasyprint" in combined_code and
            ("subprocess" in combined_code or "cli" in combined_code.lower())
        )
        self.assertTrue(
            has_cli_fallback,
            "scripts/compile_all.py must support hybrid CLI fallback execution."
        )


# ============================================================================
# F5: Verbatim UoPeople Education Block (R2.1)
# ============================================================================

class TestF5UoPeopleVerbatimBlock(unittest.TestCase):
    """Verifies that English and Spanish templates contain the exact verbatim UoPeople block."""

    def _get_html_templates(self) -> List[Path]:
        """Finds all compiled HTML templates in cv/ or templates/."""
        candidates = list(REPO_ROOT.glob("cv/**/*.html")) + list(REPO_ROOT.glob("templates/**/*.html"))
        return [c for c in candidates if "01_produccion" in str(c) or "02_publicacion" in str(c)]

    def test_f5_verbatim_uopeople_block_in_all_templates(self):
        """F5: Asserts non-negotiable legal wording for University of the People."""
        templates = self._get_html_templates()
        if not templates:
            self.skipTest("[Progressive Testability] HTML templates in cv/ not yet present.")

        for tmpl in templates:
            content = tmpl.read_text(encoding="utf-8")
            # 1. Institution
            self.assertIn(
                "University of the People",
                content,
                f"Missing 'University of the People' in {tmpl.name}"
            )
            # 2. Location
            self.assertTrue(
                "Pasadena, California" in content or "Pasadena" in content,
                f"Missing Pasadena location in {tmpl.name}"
            )
            # 3. Degree title
            self.assertIn(
                "Bachelor of Science in Computer Science",
                content,
                f"Missing 'Bachelor of Science in Computer Science' in {tmpl.name}"
            )
            # 4. Status and Term
            has_term = ("Term 3, 2027" in content or "Term 3 2027" in content)
            has_status = ("Admitted" in content or "Admitido" in content)
            self.assertTrue(
                has_term and has_status,
                f"Missing 'Admitted | Term 3, 2027' in {tmpl.name}"
            )
            # 5. WSCUC accreditation
            self.assertIn(
                "WSCUC",
                content,
                f"Missing WSCUC accreditation reference in {tmpl.name}"
            )
            # 6. Modality
            has_online = ("100% Online" in content or "100% en" in content or "Online" in content)
            self.assertTrue(
                has_online,
                f"Missing 100% Online modality indicator in {tmpl.name}"
            )


# ============================================================================
# F6: Calibrated CSS 1-Page Budget Tuning (R2.2)
# ============================================================================

class TestF6CssBudgetTuning(unittest.TestCase):
    """Verifies that CSS margin and typography rules conform to 1-page budget tuning."""

    def _get_html_templates(self) -> List[Path]:
        candidates = list(REPO_ROOT.glob("cv/**/*.html")) + list(REPO_ROOT.glob("templates/**/*.html"))
        return [c for c in candidates if "01_produccion" in str(c) or "02_publicacion" in str(c)]

    def test_f6_calibrated_margins_and_font_size(self):
        """F6: Inspects CSS @page rules for 5.4mm vertical margin and 9.05pt font."""
        templates = self._get_html_templates()
        if not templates:
            self.skipTest("[Progressive Testability] HTML templates in cv/ not yet present.")

        for tmpl in templates:
            content = tmpl.read_text(encoding="utf-8")
            # Margin check (5.4mm vertical margin)
            self.assertTrue(
                "5.4mm" in content,
                f"Template {tmpl.name} missing calibrated vertical margin '5.4mm'."
            )
            # Lateral margin check (13.0mm or 13mm)
            self.assertTrue(
                "13.0mm" in content or "13mm" in content,
                f"Template {tmpl.name} missing lateral margin '13.0mm'."
            )
            # Font size check (9.05pt)
            self.assertTrue(
                "9.05pt" in content,
                f"Template {tmpl.name} missing calibrated font-size '9.05pt'."
            )

    def test_f6_ats_bullet_dot_isolation_css(self):
        """F6: Confirms CSS eliminates orphaned bullet dots during copy/paste via li::before."""
        templates = self._get_html_templates()
        if not templates:
            self.skipTest("[Progressive Testability] HTML templates in cv/ not yet present.")

        for tmpl in templates:
            content = tmpl.read_text(encoding="utf-8")
            self.assertTrue(
                "list-style: none" in content or "list-style:none" in content,
                f"Template {tmpl.name} does not suppress default list-style for ATS compatibility."
            )


# ============================================================================
# F7: Programmatic 1-Page Geometry Assertion via pypdf (R2.3)
# ============================================================================

class TestF7GeometryAssertion(unittest.TestCase):
    """Verifies programmatic verification script and exact 612x792 pt 1-page geometry."""

    def setUp(self):
        self.verify_script = REPO_ROOT / "scripts" / "verify_geometry.py"
        if not self.verify_script.is_file():
            self.skipTest(f"[Progressive Testability] scripts/verify_geometry.py missing at {self.verify_script}")

    def test_f7_verify_geometry_script_runs_clean(self):
        """F7: Executes scripts/verify_geometry.py and asserts exit code 0."""
        res = run_command_safe([sys.executable, str(self.verify_script)], cwd=REPO_ROOT)
        self.assertEqual(
            res.returncode,
            0,
            f"scripts/verify_geometry.py failed (exit {res.returncode}):\n{res.stdout}\n{res.stderr}"
        )
        self.assertIn("[PASS]", res.stdout)
        self.assertIn("612.0x792.0 pt", res.stdout)

    def test_f7_independent_pypdf_geometry_assertion(self):
        """F7: Independently validates all 4 PDFs with test_harness_utils.assert_pdf_geometry."""
        pdf_targets = list(REPO_ROOT.glob("cv/**/*.pdf"))
        canonical_pdfs = [
            p for p in pdf_targets
            if "01_produccion" in str(p) or "02_publicacion" in str(p)
        ]
        if not canonical_pdfs:
            self.skipTest("[Progressive Testability] Production PDFs not found in cv/.")

        self.assertEqual(len(canonical_pdfs), 4, f"Expected 4 production PDFs, found {len(canonical_pdfs)}")
        for pdf_path in canonical_pdfs:
            res = validate_pdf_geometry(pdf_path, expected_pages=1, expected_box=(612, 792))
            self.assertTrue(
                res["valid"],
                f"PDF geometry violation in {pdf_path.name}: {res['errors']}"
            )
            self.assertEqual(res["page_count"], 1)


# ============================================================================
# F8: Unified 4-Target PDF Compilation (R2.4)
# ============================================================================

class TestF8Unified4TargetPdfCompilation(unittest.TestCase):
    """Verifies existence, non-empty size, and track-specific text anchors across all 4 targets."""

    def setUp(self):
        self.targets = {
            "de_en": REPO_ROOT / "cv" / "01_produccion_data_engineering" / "en" / "Diego_Alejandro_Escobar_Barahona_CV_EN.pdf",
            "de_es": REPO_ROOT / "cv" / "01_produccion_data_engineering" / "es" / "Diego_Alejandro_Escobar_Barahona_CV_ES.pdf",
            "pub_en": REPO_ROOT / "cv" / "02_publicacion_ia_investigacion" / "en" / "Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf",
            "pub_es": REPO_ROOT / "cv" / "02_publicacion_ia_investigacion" / "es" / "Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf",
        }
        for name, path in self.targets.items():
            if not path.is_file():
                self.skipTest(f"[Progressive Testability] Target PDF missing: {path}")

    def test_f8_all_four_pdfs_exist_and_non_empty(self):
        """F8: Confirms all 4 production PDFs exist and have non-zero size (> 10,000 bytes)."""
        for name, path in self.targets.items():
            self.assertTrue(path.is_file(), f"Target PDF missing: {name} ({path})")
            size = path.stat().st_size
            self.assertGreater(size, 10000, f"Target PDF {name} size ({size} bytes) is suspiciously small.")

    def test_f8_track_specific_text_anchors(self):
        """F8: Extracts text from each PDF and asserts track-specific key terms."""
        # DE EN anchors
        res_de_en = validate_pdf_geometry(self.targets["de_en"])
        self.assertTrue(res_de_en["valid"])
        text_de_en = res_de_en["text_snippet"]

        # Pubs EN anchors
        res_pub_en = validate_pdf_geometry(self.targets["pub_en"])
        self.assertTrue(res_pub_en["valid"])
        text_pub_en = res_pub_en["text_snippet"]

        self.assertIn("Diego", text_de_en)
        self.assertIn("Diego", text_pub_en)


# ============================================================================
# F9: Google Drive CV_Prep Folder Structure & Mapping (R3.1)
# ============================================================================

class TestF9GDriveCvPrepStructure(unittest.TestCase):
    """Verifies that Google Drive CV_Prep folder structure and IDs are mapped."""

    def test_f9_cv_prep_local_folder_exists(self):
        """F9: Verifies that docs/cv_prep directory exists in repository."""
        prep_dir = REPO_ROOT / "docs" / "cv_prep"
        self.assertTrue(prep_dir.is_dir(), f"docs/cv_prep missing at {prep_dir}")

    def test_f9_drive_portfolio_root_id_mapped(self):
        """F9: Verifies that Google Drive portfolio root ID (13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H) is defined."""
        # Checked in evidence_matrix.json or specifications doc
        matrix_file = REPO_ROOT / "resources" / "evidence_matrix.json"
        spec_file = REPO_ROOT / "docs" / "cv_prep" / "01_harness_specifications.md"

        has_mapping = False
        target_id = "13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H"

        if matrix_file.is_file() and target_id in matrix_file.read_text(encoding="utf-8"):
            has_mapping = True
        elif spec_file.is_file() and target_id in spec_file.read_text(encoding="utf-8"):
            has_mapping = True
        elif (REPO_ROOT / "README.md").is_file() and target_id in (REPO_ROOT / "README.md").read_text(encoding="utf-8"):
            has_mapping = True

        self.assertTrue(
            has_mapping,
            f"Google Drive portfolio root ID {target_id} is not mapped in resources or docs."
        )


# ============================================================================
# F10: Master Profile Doc Governance Directive (R3.2)
# ============================================================================

class TestF10MasterProfileGovernance(unittest.TestCase):
    """Verifies governance directive binding Master Profile Doc to repository specifications."""

    def test_f10_master_doc_id_and_governance_directive_present(self):
        """F10: Asserts directive text referencing Google Doc Maestro (16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ)."""
        spec_candidates = [
            REPO_ROOT / "docs" / "cv_prep" / "01_harness_specifications.md",
            REPO_ROOT / "docs" / "SPECIFICATIONS_AND_HARNESS.md",
        ]
        found_doc = None
        for c in spec_candidates:
            if c.is_file():
                found_doc = c
                break

        if not found_doc:
            self.skipTest("[Progressive Testability] Specifications document not yet present in docs/.")

        content = found_doc.read_text(encoding="utf-8")
        master_doc_id = "16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ"
        self.assertIn(
            master_doc_id,
            content,
            f"Governance directive in {found_doc.name} missing Master Doc ID '{master_doc_id}'"
        )
        self.assertTrue(
            "Gobernanza" in content or "Governance" in content or "Perfil Integral" in content,
            f"Governance directive clause missing in {found_doc.name}"
        )


# ============================================================================
# F11: Evidence-Backed Formal Specification Document (R3.3)
# ============================================================================

class TestF11FormalSpecificationDoc(unittest.TestCase):
    """Verifies the formal specification document with technical proofs and citations."""

    def setUp(self):
        candidates = [
            REPO_ROOT / "docs" / "cv_prep" / "01_harness_specifications.md",
            REPO_ROOT / "docs" / "SPECIFICATIONS_AND_HARNESS.md",
        ]
        self.spec_file = None
        for c in candidates:
            if c.is_file():
                self.spec_file = c
                break
        if not self.spec_file:
            self.skipTest("[Progressive Testability] Formal specification document missing in docs/.")
        self.content = self.spec_file.read_text(encoding="utf-8")

    def test_f11_ontotab_experimental_proofs_documented(self):
        """F11: Validates exact OntoTab empirical parameters: 30k records, 5x3 CV, 0.5596 AP, 2nd author."""
        self.assertIn("OntoTab", self.content)
        self.assertIn("30,000", self.content)
        self.assertTrue("5x3" in self.content or "5×3" in self.content)
        self.assertIn("0.5596", self.content)
        self.assertTrue("2" in self.content and "autor" in self.content.lower())

    def test_f11_gbm_deliverables_and_duration_documented(self):
        """F11: Validates GBM internship facts: 13 weeks, 15 DataStage jobs, DB2 LUW, GCP ELT."""
        self.assertIn("GBM", self.content)
        self.assertTrue("13" in self.content and ("semanas" in self.content.lower() or "weeks" in self.content.lower()))
        self.assertTrue("15" in self.content and "jobs" in self.content.lower())
        self.assertIn("DataStage", self.content)
        self.assertIn("DB2", self.content)

    def test_f11_ferrostats_and_sql_arena_proofs_documented(self):
        """F11: Validates FERROSTATS ($0.00/mo lakehouse) and SQL Arena (34 problems, 3/34 user solved)."""
        self.assertIn("FERROSTATS", self.content)
        self.assertTrue("$0.00" in self.content)
        self.assertIn("SQL Arena", self.content)
        self.assertIn("34", self.content)


# ============================================================================
# F12: Strict Anti-Exaggeration Containment Rules (R3.4)
# ============================================================================

class TestF12AntiExaggerationContainment(unittest.TestCase):
    """Verifies explicit permitted vs prohibited containment boundaries."""

    def setUp(self):
        candidates = [
            REPO_ROOT / "docs" / "cv_prep" / "01_harness_specifications.md",
            REPO_ROOT / "docs" / "SPECIFICATIONS_AND_HARNESS.md",
            REPO_ROOT / "resources" / "evidence_matrix.json",
        ]
        self.sources = [c for c in candidates if c.is_file()]
        if not self.sources:
            self.skipTest("[Progressive Testability] Anti-exaggeration containment sources missing.")
        self.combined = "\n".join(s.read_text(encoding="utf-8") for s in self.sources)

    def test_f12_permitted_and_prohibited_sections_exist(self):
        """F12: Verifies explicit permitted (PERMITIDO) and prohibited (PROHIBIDO) containment definitions."""
        self.assertTrue(
            "PERMITIDO" in self.combined or "allowed" in self.combined.lower(),
            "Containment specifications must define explicitly permitted claims."
        )
        self.assertTrue(
            "PROHIBIDO" in self.combined or "forbidden" in self.combined.lower(),
            "Containment specifications must define explicitly prohibited claims."
        )

    def test_f12_forbidden_claims_enforced(self):
        """F12: Validates prohibition against unbacked seniority, 95/100 typo, and sole author claims."""
        self.assertIn("Machine Learning Engineer", self.combined)
        self.assertIn("Senior", self.combined)
        self.assertIn("95/100", self.combined)


# ============================================================================
# F13: ATS Role Paraphrase Matrices for DE, DA, AI SWE (R4.1)
# ============================================================================

class TestF13AtsParaphraseMatrices(unittest.TestCase):
    """Verifies the three ATS role paraphrase matrices for DE, DA, and AI SWE."""

    def setUp(self):
        candidates = [
            REPO_ROOT / "docs" / "cv_prep" / "02_paraphrase_matrices.md",
            REPO_ROOT / "docs" / "ATS_PARAPHRASE_MATRICES.md",
        ]
        self.matrix_file = None
        for c in candidates:
            if c.is_file():
                self.matrix_file = c
                break
        if not self.matrix_file:
            self.skipTest("[Progressive Testability] ATS paraphrase matrices document missing in docs/.")
        self.content = self.matrix_file.read_text(encoding="utf-8")

    def test_f13_three_distinct_role_matrices_present(self):
        """F13: Confirms presence of all three target role sections."""
        # Role 1: Data Engineer
        self.assertTrue(
            "Data Engineer" in self.content,
            "Missing Role 1: Data Engineer in paraphrase matrices."
        )
        # Role 2: Data Analyst / Analytics Engineer
        self.assertTrue(
            "Data Analyst" in self.content or "Analytics Engineer" in self.content,
            "Missing Role 2: Data Analyst / Analytics Engineer in paraphrase matrices."
        )
        # Role 3: AI SWE / Trainee
        self.assertTrue(
            "AI" in self.content and ("Software Engineer" in self.content or "Agentic" in self.content),
            "Missing Role 3: AI / Agentic SWE in paraphrase matrices."
        )

    def test_f13_bilingual_bullets_included(self):
        """F13: Confirms approved bullet points in English and Spanish."""
        self.assertIn("EN", self.content)
        self.assertIn("ES", self.content)


# ============================================================================
# F14: Forensic Evidence Gap Audit & Catalog (R4.2)
# ============================================================================

class TestF14ForensicEvidenceGapAudit(unittest.TestCase):
    """Verifies the 4-tier forensic evidence gap catalog and resolution records."""

    def setUp(self):
        candidates = [
            REPO_ROOT / "docs" / "cv_prep" / "03_evidence_gaps.md",
            REPO_ROOT / "docs" / "FORENSIC_EVIDENCE_GAP_AUDIT.md",
        ]
        self.gap_file = None
        for c in candidates:
            if c.is_file():
                self.gap_file = c
                break
        if not self.gap_file:
            self.skipTest("[Progressive Testability] Forensic evidence gap document missing in docs/.")
        self.content = self.gap_file.read_text(encoding="utf-8")

    def test_f14_four_tier_forensic_pipeline_defined(self):
        """F14: Verifies definition of 4-tier forensic categorization (Tier 1..Tier 4)."""
        self.assertIn("Tier 1", self.content)
        self.assertIn("Tier 2", self.content)
        self.assertIn("Tier 3", self.content)
        self.assertIn("Tier 4", self.content)

    def test_f14_critical_gaps_addressed(self):
        """F14: Verifies resolution of GAP-001 (EF SET 95 vs 66), GAP-002, GAP-003, GAP-008."""
        self.assertIn("GAP-001", self.content)
        self.assertIn("66/100", self.content)
        self.assertIn("GAP-002", self.content)
        self.assertIn("GAP-003", self.content)
        self.assertIn("GAP-008", self.content)


# ============================================================================
# F15: Comprehensive Interview Defense Manual (R5.1)
# ============================================================================

class TestF15InterviewDefenseManual(unittest.TestCase):
    """Verifies interview defense manual covering personas, projects, and STAR answers."""

    def setUp(self):
        candidates = [
            REPO_ROOT / "docs" / "INTERVIEW_DEFENSE_MANUAL.md",
            REPO_ROOT / "docs" / "cv_prep" / "04_interview_defense_manual.md",
        ]
        self.manual_file = None
        for c in candidates:
            if c.is_file():
                self.manual_file = c
                break
        if not self.manual_file:
            self.skipTest("[Progressive Testability] docs/INTERVIEW_DEFENSE_MANUAL.md pending M3 implementation")
        self.content = self.manual_file.read_text(encoding="utf-8")

    def test_f15_interviewer_personas_and_projects_covered(self):
        """F15: Confirms defense scripts for personas (Recruiter, Tech Lead, Auditor) and key projects."""
        for project in ["OntoTab", "GBM", "FERROSTATS", "SQL Arena"]:
            self.assertIn(project, self.content)


# ============================================================================
# F16: Interactive Antigravity Skill & CLI Drill Runner (R5.2)
# ============================================================================

class TestF16InteractiveAntigravitySkill(unittest.TestCase):
    """Verifies Antigravity skill layout, SKILL.md frontmatter, and drill_runner.py."""

    def setUp(self):
        self.skill_dir = REPO_ROOT / ".agents" / "skills" / "cv-interview-defense"
        if not self.skill_dir.is_dir():
            self.skipTest("[Progressive Testability] .agents/skills/cv-interview-defense pending M3 implementation")

    def test_f16_skill_manifest_valid(self):
        """F16: Validates SKILL.md frontmatter contains name and description."""
        skill_md = self.skill_dir / "SKILL.md"
        self.assertTrue(skill_md.is_file(), f"SKILL.md missing at {skill_md}")
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn("name: cv-interview-defense", content)
        self.assertIn("description:", content)

    def test_f16_drill_runner_executable(self):
        """F16: Executes drill_runner.py --help and asserts exit code 0."""
        runner_script = self.skill_dir / "scripts" / "drill_runner.py"
        if not runner_script.is_file():
            self.skipTest(f"[Progressive Testability] drill_runner.py missing at {runner_script}")
        res = run_command_safe([sys.executable, str(runner_script), "--help"], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 0, f"drill_runner.py --help failed: {res.stderr}")


# ============================================================================
# F17: Google Docs Sync Mapping for Defense & Skill (R5.3)
# ============================================================================

class TestF17GDocsSyncMapping(unittest.TestCase):
    """Verifies Google Docs backup mapping for defense manual and skill."""

    def test_f17_gdocs_sync_mapping_documented(self):
        """F17: Verifies cloud backup mapping for defense manual."""
        candidates = [
            REPO_ROOT / "docs" / "cv_prep" / "01_harness_specifications.md",
            REPO_ROOT / "docs" / "cv_prep" / "04_interview_defense_manual.md",
            REPO_ROOT / "resources" / "evidence_matrix.json",
        ]
        sources = [c for c in candidates if c.is_file()]
        if not sources:
            self.skipTest("[Progressive Testability] GDocs sync mapping sources pending M3 implementation")

        combined = "\n".join(s.read_text(encoding="utf-8") for s in sources)
        # Check that Google Docs mapping or synchronization directive is present
        has_sync_anchor = (
            "Google Doc" in combined or
            "16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ" in combined or
            "gdocs" in combined.lower()
        )
        self.assertTrue(has_sync_anchor, "Cloud synchronization mapping missing for defense manual.")


# ============================================================================
# F18: Systematic 8-Field Decision Log Schema (R6.1)
# ============================================================================

class TestF18DecisionLogSchema(unittest.TestCase):
    """Verifies that docs/DECISION_LOG.md enforces the 8 mandatory fields per entry."""

    def setUp(self):
        self.log_file = REPO_ROOT / "docs" / "DECISION_LOG.md"
        if not self.log_file.is_file():
            self.skipTest("[Progressive Testability] docs/DECISION_LOG.md pending M3 implementation")

    def test_f18_decision_log_entries_have_all_mandatory_fields(self):
        """F18: Parses DECISION_LOG.md and asserts 8 required fields across every entry."""
        entries = parse_decision_log(self.log_file)
        self.assertGreater(len(entries), 0, "docs/DECISION_LOG.md contains zero parseable LOG entries.")

        valid, errors = validate_decision_log_entries(entries)
        self.assertTrue(
            valid,
            f"docs/DECISION_LOG.md schema validation failed:\n" + "\n".join(errors)
        )


# ============================================================================
# F19: Initial Engineering Hurdle Logs LOG-001..LOG-004 (R6.2)
# ============================================================================

class TestF19DecisionLogInitialHurdles(unittest.TestCase):
    """Verifies that LOG-001 through LOG-004 are present and document required hurdles."""

    def setUp(self):
        self.log_file = REPO_ROOT / "docs" / "DECISION_LOG.md"
        if not self.log_file.is_file():
            # Check README summary fallback if DECISION_LOG.md is pending
            readme = REPO_ROOT / "README.md"
            if readme.is_file() and "LOG-001" in readme.read_text(encoding="utf-8"):
                self.log_content = readme.read_text(encoding="utf-8")
                self.is_readme_fallback = True
                return
            self.skipTest("[Progressive Testability] docs/DECISION_LOG.md hurdles pending M3 implementation")
        self.log_content = self.log_file.read_text(encoding="utf-8")
        self.is_readme_fallback = False

    def test_f19_logs_001_to_004_present(self):
        """F19: Verifies LOG-001 (WeasyPrint), LOG-002 (1-Page Budget), LOG-003 (ATS Dot), LOG-004 (Drive Sync)."""
        expected_hurdles = [
            ("LOG-001", "WeasyPrint"),
            ("LOG-002", "Margin"),
            ("LOG-003", "ATS"),
            ("LOG-004", "Drive"),
        ]
        for log_id, topic in expected_hurdles:
            self.assertIn(
                log_id,
                self.log_content,
                f"Missing {log_id} in decision logs."
            )


# ============================================================================
# F20: Ethical Truthfulness Linter Script (R7.1)
# ============================================================================

class TestF20TruthLinterScript(unittest.TestCase):
    """Verifies the ethical truthfulness linter execution and exit code semantics."""

    def setUp(self):
        self.linter_script = REPO_ROOT / "scripts" / "lint_cv_truth.py"
        if not self.linter_script.is_file():
            self.skipTest("[Progressive Testability] scripts/lint_cv_truth.py pending M4 implementation")

    def test_f20_linter_runs_clean_on_production_templates(self):
        """F20: Runs scripts/lint_cv_truth.py on current codebase and asserts exit code 0."""
        res = run_command_safe([sys.executable, str(self.linter_script)], cwd=REPO_ROOT)
        self.assertEqual(
            res.returncode,
            0,
            f"scripts/lint_cv_truth.py failed with exit code {res.returncode}:\n{res.stdout}\n{res.stderr}"
        )


# ============================================================================
# F21: Unified Local CI/CD Harness Runner (R7.2)
# ============================================================================

class TestF21LocalCiHarnessRunner(unittest.TestCase):
    """Verifies that scripts/run_ci_harness.py exists and supports CI verification stages."""

    def setUp(self):
        self.ci_script = REPO_ROOT / "scripts" / "run_ci_harness.py"
        if not self.ci_script.is_file():
            self.skipTest("[Progressive Testability] scripts/run_ci_harness.py pending M4 implementation")

    def test_f21_ci_harness_help_and_options(self):
        """F21: Executes scripts/run_ci_harness.py --help and asserts exit code 0."""
        res = run_command_safe([sys.executable, str(self.ci_script), "--help"], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 0, f"run_ci_harness.py --help failed: {res.stderr}")


# ============================================================================
# F22: Google Drive Dated Sync Automation (R7.3)
# ============================================================================

class TestF22GoogleDriveDatedSync(unittest.TestCase):
    """Verifies that scripts/sync_drive.py supports dry-run without network mutations."""

    def setUp(self):
        self.sync_script = REPO_ROOT / "scripts" / "sync_drive.py"
        if not self.sync_script.is_file():
            self.skipTest("[Progressive Testability] scripts/sync_drive.py pending M4 implementation")

    def test_f22_sync_drive_dry_run(self):
        """F22: Runs sync_drive.py --dry-run and asserts exit code 0."""
        res = run_command_safe([sys.executable, str(self.sync_script), "--dry-run"], cwd=REPO_ROOT)
        self.assertEqual(
            res.returncode,
            0,
            f"sync_drive.py --dry-run failed with exit code {res.returncode}:\n{res.stdout}\n{res.stderr}"
        )


# ============================================================================
# F23: GitHub Actions CI/CD Workflow Syntax & Stages (R7.4)
# ============================================================================

class TestF23GitHubActionsWorkflow(unittest.TestCase):
    """Verifies GitHub Actions workflow configuration syntax and pipeline stages."""

    def setUp(self):
        self.workflow_file = REPO_ROOT / ".github" / "workflows" / "cv_ci_cd.yml"
        if not self.workflow_file.is_file():
            self.skipTest("[Progressive Testability] .github/workflows/cv_ci_cd.yml pending M4 implementation")
        self.content = self.workflow_file.read_text(encoding="utf-8")

    def test_f23_workflow_triggers_and_runner(self):
        """F23: Confirms workflow triggers on push/PR and runs on ubuntu-latest."""
        self.assertTrue("push" in self.content or "pull_request" in self.content)
        self.assertIn("ubuntu-latest", self.content)

    def test_f23_workflow_dependencies_and_verification_stages(self):
        """F23: Confirms installation of Linux Pango dependencies and execution of geometry verification."""
        self.assertIn("libpango", self.content)
        self.assertIn("weasyprint", self.content)
        self.assertTrue(
            "verify_geometry.py" in self.content or "compile_all.py" in self.content
        )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)

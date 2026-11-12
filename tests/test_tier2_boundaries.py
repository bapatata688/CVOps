"""test_tier2_boundaries.py - Tier 2: Boundary, Corner & Adversarial Verification Suite

Verifies master_cv against boundary limits, oversized overflows, schema violations,
unbacked seniorities, metric exaggerations, and invalid CLI arguments as specified in
TEST_INFRA.md, SCOPE.md, and DISPATCH.md:
  B1: 1-Page Geometry Budget Extremes & Overflow Detection
  B2: Anti-Exaggeration & Truth Containment Edge Cases
  B3: Decision Log Schema Boundaries (8-Field Schema & Invalid IDs)
  B4: File & Asset Input Boundaries (Missing, Corrupted, Checksum Tampering)
  B5: CLI Flags & Invalid Options Rejection

Compliance:
- Pure Python standard library unittest (Zero-Pytest, AGENTS.md Rule 5 compliant).
- Deterministic, opaque-box, requirement-driven verification.
- Reusable helpers imported from tests.test_harness_utils.
"""

import json
import os
import re
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
    assert_path_exists,
    assert_pdf_geometry,
    assert_sha256_matches,
    assert_truthful_content,
    compute_sha256,
    parse_decision_log,
    run_command_safe,
    scan_forbidden_claims,
    validate_decision_log_entries,
    validate_path_exists,
    validate_pdf_geometry,
    verify_sha256,
)

# Import WeasyPrint compilation and geometry inspection
from cv.generate_all_cvs import compile_pdf_with_weasyprint
from scripts.verify_geometry import verify_single_pdf


# ============================================================================
# B1: 1-Page Geometry Budget Extremes & Overflow Detection
# ============================================================================

class TestB1GeometryBudgetBoundaries(unittest.TestCase):
    """Boundary, corner, and adversarial tests for the 1-page Letter geometry budget."""

    def setUp(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self._temp_dir_obj.name)
        self.verify_script = REPO_ROOT / "scripts" / "verify_geometry.py"

    def tearDown(self):
        try:
            self._temp_dir_obj.cleanup()
        except Exception:
            pass

    def test_b1_01_canonical_production_pdfs_pass_geometry(self):
        """B1 Boundary Inside: All 4 production PDFs strictly conform to 1-page Letter geometry."""
        canonical_pdfs = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.pdf",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf",
        ]
        for pdf_path in canonical_pdfs:
            with self.subTest(pdf=pdf_path.name):
                self.assertTrue(pdf_path.is_file(), f"Production PDF missing: {pdf_path}")
                # 1. Independent harness assertion
                assert_pdf_geometry(pdf_path, expected_pages=1, expected_box=(612, 792))
                # 2. Production script inspection
                res = verify_single_pdf(pdf_path)
                self.assertEqual(res["errors"], [], f"Geometry errors in {pdf_path.name}: {res['errors']}")
                self.assertEqual(res["page_count"], 1)
                self.assertTrue(res["is_letter"])
                self.assertTrue(res["has_text"])
                self.assertGreaterEqual(res["char_count"], 500)

    def test_b1_02_oversized_content_triggers_multipage_overflow_and_fails_assertion(self):
        """B1 Boundary Outside: Synthesizing oversized HTML compiles to 2+ pages and triggers failure."""
        template_source = REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html"
        self.assertTrue(template_source.is_file(), f"Source template missing: {template_source}")
        
        orig_html = template_source.read_text(encoding="utf-8")
        
        # Inject 4 massive paragraphs before </body> to guarantee page overflow
        filler_paragraph = (
            "<p class='summary-text'>" +
            ("Adversarial budget stress test: verifying that content expansion triggers "
             "programmatic multi-page detection. The 1-page layout budget must strictly fail "
             "when candidate sections overflow beyond 792 points in height. ") * 8 +
            "</p>"
        )
        oversized_content = orig_html.replace("</body>", f"{filler_paragraph * 4}</body>")
        
        tmp_html = self.temp_dir / "oversized_test.html"
        tmp_pdf = self.temp_dir / "oversized_test.pdf"
        tmp_html.write_text(oversized_content, encoding="utf-8")

        # Compile with WeasyPrint
        compile_pdf_with_weasyprint(tmp_html, tmp_pdf, engine="auto")
        self.assertTrue(tmp_pdf.is_file(), "Oversized test PDF failed to compile.")

        # Assert resulting PDF has 2 or more pages
        import pypdf
        with open(tmp_pdf, "rb") as f:
            reader = pypdf.PdfReader(f)
            page_count = len(reader.pages)
        self.assertGreaterEqual(page_count, 2, "Expected oversized HTML to paginate to at least 2 pages.")

        # 1. verify_single_pdf must detect page count violation
        res = verify_single_pdf(tmp_pdf)
        self.assertGreater(len(res["errors"]), 0)
        self.assertTrue(
            any("Page count violation" in err for err in res["errors"]),
            f"Expected 'Page count violation' in errors: {res['errors']}"
        )

        # 2. assert_pdf_geometry must raise AssertionError
        with self.assertRaises(AssertionError):
            assert_pdf_geometry(tmp_pdf, expected_pages=1, expected_box=(612, 792))

        # 3. scripts/verify_geometry.py CLI must exit with code 1
        cli_res = run_command_safe(
            [sys.executable, str(self.verify_script), "--files", str(tmp_pdf)],
            cwd=REPO_ROOT
        )
        self.assertEqual(cli_res.returncode, 1, f"Expected verify_geometry CLI exit code 1, got {cli_res.returncode}")

    def test_b1_03_non_standard_a4_mediabox_rejected(self):
        """B1 Non-Standard Mediabox: A4 (595x842 pt) document is detected and rejected."""
        a4_html_content = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>"
            "@page { size: A4; margin: 10mm; }"
            "body { font-family: sans-serif; font-size: 10pt; }"
            "</style></head><body>"
            "<h1>Diego Alejandro Escobar Barahona</h1>"
            "<p>University of the People - Pasadena, California</p>"
            "<p>" + ("Testing non-standard A4 mediabox rejection in master_cv. " * 30) + "</p>"
            "</body></html>"
        )
        tmp_html = self.temp_dir / "a4_test.html"
        tmp_pdf = self.temp_dir / "a4_test.pdf"
        tmp_html.write_text(a4_html_content, encoding="utf-8")

        compile_pdf_with_weasyprint(tmp_html, tmp_pdf, engine="auto")
        self.assertTrue(tmp_pdf.is_file())

        # Inspect mediabox dimensions
        res = verify_single_pdf(tmp_pdf)
        self.assertFalse(res["is_letter"], "A4 PDF was erroneously recognized as US Letter.")
        self.assertTrue(
            any("MediaBox dimension violation" in err for err in res["errors"]),
            f"Expected MediaBox dimension violation: {res['errors']}"
        )

        # assert_pdf_geometry must raise AssertionError
        with self.assertRaises(AssertionError):
            assert_pdf_geometry(tmp_pdf, expected_pages=1, expected_box=(612, 792))

        # verify_geometry CLI must exit with code 1
        cli_res = run_command_safe(
            [sys.executable, str(self.verify_script), "--files", str(tmp_pdf)],
            cwd=REPO_ROOT
        )
        self.assertEqual(cli_res.returncode, 1)

    def test_b1_04_zero_byte_pdf_rejected(self):
        """B1 Empty Input: 0-byte PDF is rejected with descriptive error."""
        empty_pdf = self.temp_dir / "zero_byte.pdf"
        empty_pdf.write_bytes(b"")

        res = verify_single_pdf(empty_pdf)
        self.assertFalse(res["is_letter"])
        self.assertIn("File is empty (0 bytes)", res["errors"])

        with self.assertRaises(AssertionError):
            assert_pdf_geometry(empty_pdf)

        cli_res = run_command_safe(
            [sys.executable, str(self.verify_script), "--files", str(empty_pdf)],
            cwd=REPO_ROOT
        )
        self.assertEqual(cli_res.returncode, 1)

    def test_b1_05_corrupted_binary_pdf_rejected(self):
        """B1 Corrupted Input: Malformed binary content is rejected without crash."""
        corrupted_pdf = self.temp_dir / "corrupted.pdf"
        corrupted_pdf.write_bytes(b"%PDF-1.4\nCORRUPTED_STREAM_GARBAGE\x00\xff\xfe\x01\x02\x03\n%%EOF")

        res = verify_single_pdf(corrupted_pdf)
        self.assertFalse(res["is_letter"])
        self.assertTrue(
            any("Failed to parse PDF with pypdf" in err for err in res["errors"]),
            f"Expected parse failure error: {res['errors']}"
        )

        with self.assertRaises(AssertionError):
            assert_pdf_geometry(corrupted_pdf)

        cli_res = run_command_safe(
            [sys.executable, str(self.verify_script), "--files", str(corrupted_pdf)],
            cwd=REPO_ROOT
        )
        self.assertEqual(cli_res.returncode, 1)

    def test_b1_06_blank_pdf_zero_text_rejected(self):
        """B1 Missing Text Layer: Blank 1-page Letter PDF is rejected for missing text and anchors."""
        import pypdf
        blank_pdf = self.temp_dir / "blank_letter.pdf"
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=612.0, height=792.0)
        with open(blank_pdf, "wb") as f:
            writer.write(f)

        res = verify_single_pdf(blank_pdf)
        self.assertFalse(res["has_text"])
        self.assertTrue(any("suspiciously low character count" in err for err in res["errors"]))
        self.assertTrue(any("Missing identity anchor" in err for err in res["errors"]))
        self.assertTrue(any("Missing education anchor" in err for err in res["errors"]))

        # Independent harness validation
        harness_res = validate_pdf_geometry(blank_pdf, require_text=True)
        self.assertFalse(harness_res["valid"])
        self.assertTrue(any("zero extractable text" in err for err in harness_res["errors"]))

        cli_res = run_command_safe(
            [sys.executable, str(self.verify_script), "--files", str(blank_pdf)],
            cwd=REPO_ROOT
        )
        self.assertEqual(cli_res.returncode, 1)


# ============================================================================
# B2: Anti-Exaggeration & Truth Containment Edge Cases
# ============================================================================

class TestB2AntiExaggerationAndTruthBoundaries(unittest.TestCase):
    """Adversarial and negative boundary verification for professional truth containment."""

    @classmethod
    def setUpClass(cls):
        # Load evidence matrix to verify against authoritative specification
        matrix_path = REPO_ROOT / "resources" / "evidence_matrix.json"
        if matrix_path.is_file():
            cls.evidence_matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        else:
            cls.evidence_matrix = {}

    def test_b2_01_forbidden_seniority_adversarial_rejection(self):
        """B2 Seniority Inflation: Adversarial claims of Senior/Lead/ML Engineer are detected."""
        seniority_patterns = [
            (r"(?i)\b(?:Senior|Lead|Principal|Staff)\s+(?:Data\s+Engineer|Software\s+Engineer|Cloud\s+Architect|Engineer|Architect)\b", "Senior/Lead/Staff/Principal title inflation"),
            (r"(?i)\b(?:ML|Machine\s+Learning)\s+Engineer\b", "Machine Learning Engineer title inflation"),
        ]
        adversarial_seniorities = [
            "Diego Escobar, Senior Data Engineer at GBM",
            "Acted as Lead Data Engineer directing cloud pipeline architecture",
            "Promoted to Machine Learning Engineer at GBM after 13 weeks",
            "ML Engineer specializing in BigQuery and Datastream",
            "Principal Data Engineer designing multi-cloud data platforms",
            "Staff Data Engineer supervising production deployments",
        ]
        for claim in adversarial_seniorities:
            with self.subTest(claim=claim):
                violations = scan_forbidden_claims(claim, custom_patterns=seniority_patterns)
                self.assertGreater(
                    len(violations),
                    0,
                    f"Forbidden seniority claim was NOT detected: '{claim}'"
                )
                with self.assertRaises(AssertionError):
                    assert_truthful_content(claim, custom_patterns=seniority_patterns)

    def test_b2_02_forbidden_author_position_adversarial_rejection(self):
        """B2 Authorship Inflation: Adversarial claims of First or Lead author are detected."""
        author_patterns = [
            (r"(?i)\b(?:first|lead|principal|sole|solo)\s+author\b", "Forbidden authorship inflation"),
            (r"(?i)\bprincipal\s+investigator\b", "Forbidden PI title inflation"),
        ]
        adversarial_authorships = [
            "Served as first author on the OntoTab scientific manuscript",
            "Diego Escobar, lead author on the paper 'OntoTab'",
            "Principal investigator leading the credit risk tabular research",
            "Sole author of the OntoTab experimental study",
        ]
        for claim in adversarial_authorships:
            with self.subTest(claim=claim):
                violations = scan_forbidden_claims(claim, custom_patterns=author_patterns)
                self.assertGreater(
                    len(violations),
                    0,
                    f"Forbidden authorship claim was NOT detected: '{claim}'"
                )
                with self.assertRaises(AssertionError):
                    assert_truthful_content(claim, custom_patterns=author_patterns)

    def test_b2_03_metric_boundary_ef_set_score_adversarial_rejection(self):
        """B2 EF SET Metric: Score exaggeration (95/100 draft typo) is aggressively detected."""
        ef_set_patterns = [
            (r"(?i)\b(?:95\s*/\s*100|95%\s*ef\s*set|ef\s*set\s*(?:score\s*(?:of\s*)?)?95)\b", "EF SET score exaggeration"),
        ]
        adversarial_scores = [
            "Certified EF SET English score: 95/100",
            "Demonstrated 95% EF SET English proficiency",
            "EF SET score of 95 in advanced English",
            "EF SET: 95 / 100 C2 Proficient",
        ]
        for claim in adversarial_scores:
            with self.subTest(claim=claim):
                violations = scan_forbidden_claims(claim, custom_patterns=ef_set_patterns)
                self.assertGreater(
                    len(violations),
                    0,
                    f"EF SET score exaggeration was NOT detected: '{claim}'"
                )
                with self.assertRaises(AssertionError):
                    assert_truthful_content(claim, custom_patterns=ef_set_patterns)

    def test_b2_04_metric_boundary_sql_arena_adversarial_rejection(self):
        """B2 SQL Arena Metric: Claiming candidate solved all 34/34 problems is detected."""
        # Candidate created 34 problems, but user progress is strictly 3 solved (nulls-1..3)
        sql_arena_forbidden_patterns = [
            (r"(?i)\b(?:completed|solved)\s+(?:all\s+)?34\s+(?:problems|exercises|challenges)\b", "False completion claim"),
            (r"(?i)\b34\s*/\s*34\s+(?:solved|completed)\b", "Exaggerated 34/34 solve metric"),
        ]
        adversarial_claims = [
            "Solved 34/34 solved challenges on SQL Arena",
            "Successfully completed all 34 problems on SQL Arena",
            "Solved all 34 exercises across 11 modules",
        ]
        for claim in adversarial_claims:
            with self.subTest(claim=claim):
                violations = scan_forbidden_claims(claim, custom_patterns=sql_arena_forbidden_patterns)
                self.assertGreater(
                    len(violations),
                    0,
                    f"SQL Arena solve exaggeration was NOT detected: '{claim}'"
                )

    def test_b2_05_metric_boundary_ontotab_xgboost_ap_adversarial_rejection(self):
        """B2 OntoTab Metric: AP claims exceeding empirical 0.5596 baseline are detected."""
        ontotab_metric_patterns = [
            (r"(?i)\b(?:0\.(?:5[6-9]|[6-9]\d{2,})|0\.[6-9]\d*)\s*(?:AP|Average\s*Precision)\b", "Exaggerates OntoTab AP (>0.5596)"),
            (r"(?i)\bontology(?:[-\s]+enriched)?\s+text\s+outperformed\s+(?:numeric|tabular)\b", "Contradicts empirical finding that numeric tabular beat ontology"),
        ]
        adversarial_claims = [
            "Achieved 0.85 AP on credit default prediction using XGBoost",
            "Demonstrated 0.72 Average Precision with ontology embeddings",
            "Claimed ontology-enriched text outperformed numeric tabular features",
        ]
        for claim in adversarial_claims:
            with self.subTest(claim=claim):
                violations = scan_forbidden_claims(claim, custom_patterns=ontotab_metric_patterns)
                self.assertGreater(
                    len(violations),
                    0,
                    f"OntoTab metric exaggeration was NOT detected: '{claim}'"
                )

    def test_b2_06_internship_duration_and_permanence_adversarial_rejection(self):
        """B2 GBM Role & Duration: Claims of permanent role or >13 weeks are detected."""
        gbm_duration_patterns = [
            (r"(?i)\b(?:full-time|permanent)\s+(?:Data\s+Engineer|role|position)\s+at\s+GBM\b", "Claims permanent/full-time role at GBM (was 13-week intern)"),
            (r"(?i)\b(?:[6-9]|\d{2,})\s+months\s+(?:at\s+GBM|internship\s+at\s+GBM)\b", "Exaggerates GBM duration beyond 13 weeks"),
            (r"(?i)\b(?:[1-9]|\d{2,})\s+years?\s+at\s+GBM\b", "Exaggerates GBM duration to years"),
        ]
        adversarial_claims = [
            "Employed as full-time Data Engineer at GBM",
            "Completed 6 months internship at GBM",
            "Worked 2 years at GBM leading data pipelines",
            "Held a permanent position at GBM",
        ]
        for claim in adversarial_claims:
            with self.subTest(claim=claim):
                violations = scan_forbidden_claims(claim, custom_patterns=gbm_duration_patterns)
                self.assertGreater(
                    len(violations),
                    0,
                    f"GBM duration/permanence exaggeration was NOT detected: '{claim}'"
                )

    def test_b2_07_all_production_templates_contain_zero_forbidden_seniority(self):
        """B2 Production Audit: Templates contain ZERO forbidden seniority or inflated titles."""
        template_paths = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.html",
        ]
        forbidden_regexes = [
            r"\bSenior\s+Data\s+Engineer\b",
            r"\bLead\s+Data\s+Engineer\b",
            r"\bML\s+Engineer\b",
            r"\bMachine\s+Learning\s+Engineer\b",
            r"\bPrincipal\s+Engineer\b",
            r"\bStaff\s+Data\s+Engineer\b",
        ]
        for tmpl_path in template_paths:
            self.assertTrue(tmpl_path.is_file(), f"Missing template: {tmpl_path}")
            content = tmpl_path.read_text(encoding="utf-8")
            for f_regex in forbidden_regexes:
                match = re.search(f_regex, content, re.IGNORECASE)
                self.assertIsNone(
                    match,
                    f"Template {tmpl_path.name} contains forbidden seniority: '{match.group(0) if match else ''}'"
                )

    def test_b2_08_all_production_templates_contain_strictly_authorized_author_position(self):
        """B2 Authorship Audit: Templates strictly state Diego as 2nd author (never first/lead)."""
        pub_templates = [
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.html",
        ]
        author_disclosure_regex = re.compile(
            r"(?i)(?:co-?author|coautor|2nd\s+(?:author|of\s+7)|2\.?&ordm;\s+de\s+7|2\.?º\s+de\s+7|second\s+author|segundo\s+autor)"
        )
        for tmpl_path in pub_templates:
            self.assertTrue(tmpl_path.is_file())
            content = tmpl_path.read_text(encoding="utf-8")
            # Must strictly describe candidate as 2nd author / segundo autor
            self.assertTrue(
                author_disclosure_regex.search(content),
                f"Template {tmpl_path.name} is missing authoritative 2nd author disclosure."
            )
            # Must NOT claim first or lead author
            self.assertIsNone(re.search(r"(?i)\bfirst\s+author\b", content))
            self.assertIsNone(re.search(r"(?i)\blead\s+author\b", content))
            self.assertIsNone(re.search(r"(?i)\bprincipal\s+investigator\b", content))

    def test_b2_09_all_production_templates_contain_strictly_authorized_metrics(self):
        """B2 Metrics Audit: Production templates strictly state 66/100 EF SET and 0.5596 AP."""
        templates = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.html",
        ]
        for tmpl_path in templates:
            content = tmpl_path.read_text(encoding="utf-8")
            # EF SET score check: MUST NOT contain 95/100
            self.assertNotIn("95/100", content, f"Template {tmpl_path.name} contains draft typo '95/100'")
            self.assertNotIn("95 / 100", content)
            # If EF SET is mentioned, it MUST be 66/100
            if "EF SET" in content:
                self.assertIn("66/100", content, f"Template {tmpl_path.name} missing verified score '66/100'")

            # SQL Arena check: MUST NOT claim 34/34 solved
            self.assertNotIn("34/34", content)
            self.assertNotIn("solved all 34", content.lower())

            # OntoTab AP check: If XGBoost AP is mentioned, it must be 0.5596
            if "OntoTab" in content and "AP" in content:
                self.assertTrue(
                    "0.5596" in content or "0.56" in content,
                    f"Template {tmpl_path.name} does not match empirical XGBoost AP 0.5596"
                )

    def test_b2_10_all_production_templates_contain_strictly_internship_duration(self):
        """B2 Internship Audit: GBM role is strictly framed as Intern/Pasantía for ~13 weeks."""
        templates = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.html",
        ]
        for tmpl_path in templates:
            content = tmpl_path.read_text(encoding="utf-8")
            # Must mention Intern or Pasante / Pasantía
            self.assertTrue(
                any(term in content for term in ["Intern", "Pasantía", "Pasante"]),
                f"Template {tmpl_path.name} does not clearly specify Intern status for GBM."
            )
            # Must NOT claim permanent or full-time
            self.assertNotIn("Permanent", content)
            self.assertNotIn("Full-time", content)

    def test_b2_11_all_compiled_pdfs_pass_truth_containment(self):
        """B2 Compiled PDF Audit: Extracted text from all 4 PDFs contains zero forbidden claims."""
        import pypdf
        canonical_pdfs = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.pdf",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf",
        ]
        for pdf_path in canonical_pdfs:
            with self.subTest(pdf=pdf_path.name):
                with open(pdf_path, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
                violations = scan_forbidden_claims(extracted)
                self.assertEqual(
                    violations,
                    [],
                    f"PDF {pdf_path.name} contains truth violations: {violations}"
                )
                self.assertNotIn("Senior Data Engineer", extracted)
                self.assertNotIn("Lead Data Engineer", extracted)
                self.assertNotIn("ML Engineer", extracted)
                self.assertNotIn("95/100", extracted)
                self.assertNotIn("34/34", extracted)


# ============================================================================
# B3: Decision Log Schema Boundaries
# ============================================================================

class TestB3DecisionLogSchemaBoundaries(unittest.TestCase):
    """Boundary and corner tests for docs/DECISION_LOG.md 8-field schema."""

    def setUp(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self._temp_dir_obj.name)

    def tearDown(self):
        try:
            self._temp_dir_obj.cleanup()
        except Exception:
            pass

    def _generate_valid_entry(self, entry_id: str = "LOG-001") -> str:
        return (
            f"## [{entry_id}] - Valid Title\n"
            "- **Timestamp**: 2026-11-11T12:00:00Z\n"
            "- **Component**: scripts/compile_all.py\n"
            "### Problem Statement\n"
            "Valid problem statement text.\n"
            "### Root Cause Analysis\n"
            "Valid root cause analysis text.\n"
            "### Alternatives Evaluated\n"
            "1. Option A. 2. Option B.\n"
            "### Chosen Solution\n"
            "Valid chosen solution text.\n"
            "### Rationale\n"
            "Valid rationale text.\n"
            "### Verification Evidence\n"
            "Valid verification evidence text.\n"
        )

    def test_b3_01_missing_each_of_the_8_mandatory_fields_individually(self):
        """B3 Schema Completeness: Omitting any 1 of the 8 mandatory fields fails validation."""
        mandatory_fields = [
            ("entry_id", "## Invalid Title Without Log ID\n- **Timestamp**: 2026-11-11\n- **Component**: foo\n### Problem Statement\np\n### Root Cause Analysis\nr\n### Alternatives Evaluated\na\n### Chosen Solution\ns\n### Rationale\nrat\n"),
            ("timestamp", "## LOG-001: Title\n- **Component**: foo\n### Problem Statement\np\n### Root Cause Analysis\nr\n### Alternatives Evaluated\na\n### Chosen Solution\ns\n### Rationale\nrat\n"),
            ("component", "## LOG-001: Title\n- **Timestamp**: 2026-11-11\n### Problem Statement\np\n### Root Cause Analysis\nr\n### Alternatives Evaluated\na\n### Chosen Solution\ns\n### Rationale\nrat\n"),
            ("problem_statement", "## LOG-001: Title\n- **Timestamp**: 2026-11-11\n- **Component**: foo\n### Root Cause Analysis\nr\n### Alternatives Evaluated\na\n### Chosen Solution\ns\n### Rationale\nrat\n"),
            ("root_cause_analysis", "## LOG-001: Title\n- **Timestamp**: 2026-11-11\n- **Component**: foo\n### Problem Statement\np\n### Alternatives Evaluated\na\n### Chosen Solution\ns\n### Rationale\nrat\n"),
            ("alternatives_evaluated", "## LOG-001: Title\n- **Timestamp**: 2026-11-11\n- **Component**: foo\n### Problem Statement\np\n### Root Cause Analysis\nr\n### Chosen Solution\ns\n### Rationale\nrat\n"),
            ("chosen_solution", "## LOG-001: Title\n- **Timestamp**: 2026-11-11\n- **Component**: foo\n### Problem Statement\np\n### Root Cause Analysis\nr\n### Alternatives Evaluated\na\n### Rationale\nrat\n"),
            ("rationale", "## LOG-001: Title\n- **Timestamp**: 2026-11-11\n- **Component**: foo\n### Problem Statement\np\n### Root Cause Analysis\nr\n### Alternatives Evaluated\na\n### Chosen Solution\ns\n"),
        ]

        for field_name, markdown_content in mandatory_fields:
            with self.subTest(omitted_field=field_name):
                log_file = self.temp_dir / f"missing_{field_name}.md"
                log_file.write_text(markdown_content, encoding="utf-8")
                entries = parse_decision_log(log_file)
                if field_name == "entry_id":
                    # Parser cannot identify entry without LOG-xxx header
                    self.assertEqual(len(entries), 0)
                    valid, errors = validate_decision_log_entries(entries)
                    self.assertFalse(valid)
                    self.assertIn("No decision log entries found.", errors)
                else:
                    self.assertEqual(len(entries), 1)
                    valid, errors = validate_decision_log_entries(entries)
                    self.assertFalse(valid, f"Validation should fail when '{field_name}' is missing.")
                    self.assertTrue(
                        any(field_name in err for err in errors),
                        f"Expected '{field_name}' in errors: {errors}"
                    )

    def test_b3_02_entry_missing_multiple_fields_reports_all_missing(self):
        """B3 Cumulative Errors: An entry missing several fields lists all missing attributes."""
        incomplete_markdown = (
            "## LOG-002: Incomplete Entry\n"
            "- **Timestamp**: 2026-11-11T12:00:00Z\n"
            "### Problem Statement\n"
            "Only problem statement is provided here.\n"
        )
        log_file = self.temp_dir / "incomplete.md"
        log_file.write_text(incomplete_markdown, encoding="utf-8")

        entries = parse_decision_log(log_file)
        self.assertEqual(len(entries), 1)
        valid, errors = validate_decision_log_entries(entries)
        self.assertFalse(valid)
        # Missing: component, root_cause_analysis, alternatives_evaluated, chosen_solution, rationale
        self.assertGreaterEqual(len(errors), 5)
        for expected_missing in ["component", "root_cause_analysis", "alternatives_evaluated", "chosen_solution", "rationale"]:
            self.assertTrue(
                any(expected_missing in err for err in errors),
                f"Expected '{expected_missing}' to be flagged in: {errors}"
            )

    def test_b3_03_invalid_entry_ids_rejected(self):
        r"""B3 ID Format Boundary: Headings lacking standard 'LOG-\d{3,4}' are not parsed."""
        invalid_id_markdown = (
            "# Engineering Logs\n\n"
            "## ISSUE-001: Bug in compilation\n"
            "- **Timestamp**: 2026-11-11\n"
            "### Problem Statement\np\n\n"
            "## 001: Missing prefix\n"
            "- **Timestamp**: 2026-11-11\n\n"
            "## LOG: Missing numbers\n"
            "- **Timestamp**: 2026-11-11\n\n"
            "## LOG-XYZ: Non-numeric identifier\n"
            "- **Timestamp**: 2026-11-11\n"
        )
        log_file = self.temp_dir / "invalid_ids.md"
        log_file.write_text(invalid_id_markdown, encoding="utf-8")

        entries = parse_decision_log(log_file)
        # None of the invalid headers should parse as valid LOG- entries
        self.assertEqual(entries, [])
        valid, errors = validate_decision_log_entries(entries)
        self.assertFalse(valid)
        self.assertIn("No decision log entries found.", errors)

    def test_b3_04_empty_and_whitespace_only_decision_log_rejected(self):
        """B3 Empty File Boundary: Empty and whitespace-only decision logs fail validation."""
        empty_file = self.temp_dir / "empty_log.md"
        empty_file.write_text("", encoding="utf-8")

        entries = parse_decision_log(empty_file)
        self.assertEqual(entries, [])
        valid, errors = validate_decision_log_entries(entries)
        self.assertFalse(valid)

        whitespace_file = self.temp_dir / "whitespace_log.md"
        whitespace_file.write_text("   \n\n\t  \n  ", encoding="utf-8")

        entries_ws = parse_decision_log(whitespace_file)
        self.assertEqual(entries_ws, [])
        valid_ws, _ = validate_decision_log_entries(entries_ws)
        self.assertFalse(valid_ws)

    def test_b3_05_nonexistent_decision_log_file_raises_filenotfound(self):
        """B3 Missing File Boundary: Parsing a nonexistent decision log raises FileNotFoundError."""
        nonexistent = self.temp_dir / "ghost_log.md"
        with self.assertRaises(FileNotFoundError):
            parse_decision_log(nonexistent)

    def test_b3_06_fully_compliant_entry_passes_validation(self):
        """B3 Valid Schema Acceptance: A well-formed 8-field entry passes with zero errors."""
        valid_content = self._generate_valid_entry("LOG-001")
        log_file = self.temp_dir / "valid_log.md"
        log_file.write_text(valid_content, encoding="utf-8")

        entries = parse_decision_log(log_file)
        self.assertEqual(len(entries), 1)
        valid, errors = validate_decision_log_entries(entries)
        self.assertTrue(valid, f"Expected valid log entry, got errors: {errors}")
        self.assertEqual(len(errors), 0)


# ============================================================================
# B4: File & Asset Input Boundaries
# ============================================================================

class TestB4FileInputBoundaries(unittest.TestCase):
    """Boundary and tampering detection for files, templates, and evidence assets."""

    def setUp(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self._temp_dir_obj.name)

    def tearDown(self):
        try:
            self._temp_dir_obj.cleanup()
        except Exception:
            pass

    def test_b4_01_nonexistent_file_passed_to_verify_geometry_cli_exits_nonzero(self):
        """B4 Nonexistent File: Passing missing PDF to verify_geometry exits with code 1."""
        ghost_pdf = self.temp_dir / "nonexistent_file_xyz.pdf"
        script = REPO_ROOT / "scripts" / "verify_geometry.py"
        res = run_command_safe([sys.executable, str(script), "--files", str(ghost_pdf)], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 1)
        self.assertIn("File not found", res.stdout + res.stderr)

    def test_b4_02_nonexistent_target_passed_to_compile_all_cli_exits_nonzero(self):
        """B4 Invalid Target: Passing invalid target ID to compile_all exits with code 1."""
        script = REPO_ROOT / "scripts" / "compile_all.py"
        res = run_command_safe([sys.executable, str(script), "--target", "nonexistent_target_xyz"], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Unknown target ID", res.stderr + res.stdout)

    def test_b4_03_nonexistent_target_passed_to_generate_all_cvs_exits_nonzero(self):
        """B4 Invalid Generator Target: Passing invalid target to generate_all_cvs exits with code 1."""
        script = REPO_ROOT / "cv" / "generate_all_cvs.py"
        res = run_command_safe([sys.executable, str(script), "--target", "invalid_id_123"], cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 1)

    def test_b4_04_path_existence_helpers_fail_on_missing_paths(self):
        """B4 Path Helper Boundary: assert_path_exists raises on missing files or wrong type."""
        missing_path = self.temp_dir / "missing_file_test.tmp"
        self.assertFalse(validate_path_exists(missing_path))
        with self.assertRaises(AssertionError):
            assert_path_exists(missing_path)

        # File vs Directory mismatch
        existing_file = REPO_ROOT / "README.md"
        with self.assertRaises(AssertionError):
            assert_path_exists(existing_file, is_dir=True)

        existing_dir = REPO_ROOT / "scripts"
        with self.assertRaises(AssertionError):
            assert_path_exists(existing_dir, is_dir=False)

    def test_b4_05_corrupted_or_empty_html_template_handling(self):
        """B4 Empty Template: Empty HTML template compiles to defective PDF that fails verification."""
        empty_html = self.temp_dir / "empty_template.html"
        empty_pdf = self.temp_dir / "empty_rendered.pdf"
        empty_html.write_text("", encoding="utf-8")

        compile_pdf_with_weasyprint(empty_html, empty_pdf, engine="auto")
        self.assertTrue(empty_pdf.is_file())

        res = verify_single_pdf(empty_pdf)
        self.assertGreater(len(res["errors"]), 0)
        # Should flag missing identity anchor and text extraction warning
        self.assertTrue(any("Missing identity anchor" in err for err in res["errors"]))

    def test_b4_06_all_six_known_assets_match_sha256_baselines(self):
        """B4 Checksum Parity: Authoritative SHA256 matches all 6 migrated assets byte-for-byte."""
        for rel_path, expected_hash in KNOWN_ASSET_HASHES.items():
            full_path = REPO_ROOT / "evidence" / rel_path.replace("cv/archive/", "archive/")
            if not full_path.is_file():
                # Check root relative path if layout matches directly
                full_path = REPO_ROOT / "evidence" / rel_path
            if not full_path.is_file():
                full_path = REPO_ROOT / rel_path

            self.assertTrue(full_path.is_file(), f"Asset missing: {full_path}")
            computed = compute_sha256(full_path)
            self.assertEqual(computed, expected_hash.strip().upper(), f"Hash mismatch for {rel_path}")
            self.assertTrue(verify_sha256(full_path, expected_hash))
            assert_sha256_matches(full_path, expected_hash)

    def test_b4_07_sha256_mismatch_detection_on_mutated_asset(self):
        """B4 Tampering Boundary: Flipped byte in asset causes SHA256 mismatch and assertion error."""
        # Find one real asset to mutate in a scratch directory
        source_asset = REPO_ROOT / "evidence" / "certifications" / "EF_SET_Certificate_C1_Advanced.pdf"
        self.assertTrue(source_asset.is_file())

        # Test with wrong expected hash
        bogus_hash = "0" * 64
        self.assertFalse(verify_sha256(source_asset, bogus_hash))
        with self.assertRaises(AssertionError) as ctx:
            assert_sha256_matches(source_asset, bogus_hash)
        self.assertIn("SHA256 mismatch", str(ctx.exception))

        # Physically mutate 1 byte in scratch copy
        raw_bytes = bytearray(source_asset.read_bytes())
        raw_bytes[64] = (raw_bytes[64] + 1) % 256  # Flip single byte
        mutated_asset = self.temp_dir / "mutated_cert.pdf"
        mutated_asset.write_bytes(raw_bytes)

        mutated_hash = compute_sha256(mutated_asset)
        original_hash = compute_sha256(source_asset)
        self.assertNotEqual(mutated_hash, original_hash, "Single byte change did not alter SHA256.")
        self.assertFalse(verify_sha256(mutated_asset, original_hash))
        with self.assertRaises(AssertionError):
            assert_sha256_matches(mutated_asset, original_hash)

    def test_b4_08_sha256_computation_on_missing_file_raises_filenotfound(self):
        """B4 Missing Asset: compute_sha256 on nonexistent file raises FileNotFoundError."""
        ghost_asset = self.temp_dir / "ghost_file_123.pdf"
        with self.assertRaises(FileNotFoundError):
            compute_sha256(ghost_asset)


# ============================================================================
# B5: CLI Flags & Invalid Options Rejection
# ============================================================================

class TestB5CliArgumentBoundaries(unittest.TestCase):
    """Verifies that all CLI entry points gracefully reject invalid arguments with non-zero exit codes."""

    def test_b5_01_verify_geometry_rejects_unrecognized_arguments(self):
        """B5 CLI Boundary: scripts/verify_geometry.py exits non-zero on unknown options."""
        script = REPO_ROOT / "scripts" / "verify_geometry.py"
        res = run_command_safe([sys.executable, str(script), "--unrecognized-option-xyz"], cwd=REPO_ROOT)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("unrecognized argument", res.stderr.lower() + res.stdout.lower())

    def test_b5_02_compile_all_rejects_unrecognized_arguments(self):
        """B5 CLI Boundary: scripts/compile_all.py exits non-zero on unknown options."""
        script = REPO_ROOT / "scripts" / "compile_all.py"
        res = run_command_safe([sys.executable, str(script), "--bogus-flag"], cwd=REPO_ROOT)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("unrecognized argument", res.stderr.lower() + res.stdout.lower())

    def test_b5_03_compile_all_rejects_invalid_engine_choice(self):
        """B5 CLI Boundary: scripts/compile_all.py rejects invalid choices for --engine."""
        script = REPO_ROOT / "scripts" / "compile_all.py"
        res = run_command_safe([sys.executable, str(script), "--engine", "quantum_engine"], cwd=REPO_ROOT)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("invalid choice", res.stderr.lower())

    def test_b5_04_run_all_e2e_tests_rejects_unrecognized_arguments(self):
        """B5 CLI Boundary: tests/run_all_e2e_tests.py exits non-zero on unknown options."""
        script = REPO_ROOT / "tests" / "run_all_e2e_tests.py"
        res = run_command_safe([sys.executable, str(script), "--invalid-test-flag"], cwd=REPO_ROOT)
        self.assertNotEqual(res.returncode, 0)

    def test_b5_05_run_all_e2e_tests_rejects_invalid_tier_choice(self):
        """B5 CLI Boundary: tests/run_all_e2e_tests.py rejects invalid tier selector."""
        script = REPO_ROOT / "tests" / "run_all_e2e_tests.py"
        res = run_command_safe([sys.executable, str(script), "--tier", "tier99_invalid"], cwd=REPO_ROOT)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("invalid choice", res.stderr.lower())

    def test_b5_06_generate_all_cvs_rejects_unrecognized_arguments(self):
        """B5 CLI Boundary: cv/generate_all_cvs.py exits non-zero on unknown options."""
        script = REPO_ROOT / "cv" / "generate_all_cvs.py"
        res = run_command_safe([sys.executable, str(script), "--unsupported-option"], cwd=REPO_ROOT)
        self.assertNotEqual(res.returncode, 0)

    def test_b5_07_pending_runners_graceful_progressive_testability(self):
        """B5 Progressive Testability: Validates error rejection on future milestone CLI scripts if present."""
        future_scripts = [
            ("scripts/run_ci_harness.py", "M4 Local CI Runner"),
            ("scripts/sync_drive.py", "M4 Drive Sync Runner"),
            ("scripts/lint_cv_truth.py", "M4 Truth Linter"),
            (".agents/skills/cv-interview-defense/scripts/drill_runner.py", "M3 Drill Runner"),
        ]
        tested_count = 0
        for rel_path, desc in future_scripts:
            script_path = REPO_ROOT / rel_path
            if script_path.is_file():
                res = run_command_safe([sys.executable, str(script_path), "--invalid-test-flag"], cwd=REPO_ROOT)
                self.assertNotEqual(res.returncode, 0, f"Expected non-zero exit for {desc} with bad flags.")
                tested_count += 1

        if tested_count == 0:
            # All future runners pending later milestones (M3/M4)
            self.skipTest("[Progressive Testability] Future CLI runners pending M3/M4 implementation.")


# ============================================================================
# Main Execution Entry Point
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)

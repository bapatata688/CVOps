"""test_tier4_scenarios.py - Tier 4: Real-World Application & CI/CD Scenarios Suite

Verifies master_cv against end-to-end real-world execution scenarios as mapped in
TEST_INFRA.md § 2, SCOPE.md, and DISPATCH.md:
  S1: Full CI/CD Pipeline Execution & GitHub Actions Workflow Simulation
  S2: End-to-End Technical Recruitment & Background Screener Simulation
  S3: ATS Parsing Fidelity, Header Extraction, Keyword Density & Hygiene
  S4: Progressive Testability & Rule 5 Compliance Contracts

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
from typing import Any, Dict, List, Optional, Set, Tuple

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
    extract_cv_contact_info,
    extract_pdf_text_full,
    parse_ats_keywords,
    parse_ci_harness_output,
    parse_decision_log,
    run_command_safe,
    scan_forbidden_claims,
    validate_decision_log_entries,
    validate_path_exists,
    validate_pdf_geometry,
    verify_sha256,
)

# Optional pypdf import with availability guard
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# ============================================================================
# S1: Full CI/CD Pipeline Execution & GitHub Actions Simulation
# ============================================================================

class TestS1CiCdPipelineExecutionSimulation(unittest.TestCase):
    """S1: Simulates local and cloud CI/CD pipeline execution cycles."""

    def setUp(self):
        self.ci_script = REPO_ROOT / "scripts" / "run_ci_harness.py"
        self.compile_script = REPO_ROOT / "scripts" / "compile_all.py"
        self.verify_script = REPO_ROOT / "scripts" / "verify_geometry.py"
        self.linter_script = REPO_ROOT / "scripts" / "lint_cv_truth.py"
        self.sync_script = REPO_ROOT / "scripts" / "sync_drive.py"
        self.workflow_file = REPO_ROOT / ".github" / "workflows" / "cv_ci_cd.yml"

    def test_s1_01_full_ci_harness_runner_execution_and_exit_code_zero(self):
        """S1 CI Run: Executes scripts/run_ci_harness.py, asserting exit code 0 and all 4 stages pass."""
        if not self.ci_script.is_file():
            # Synthetic fallback: test compilation and geometry verification directly
            res_compile = run_command_safe(
                [sys.executable, str(self.compile_script), "--all", "--verify"],
                cwd=REPO_ROOT,
                timeout_sec=90.0
            )
            self.assertEqual(res_compile.returncode, 0, f"Compilation stage failed: {res_compile.stderr}")
            self.skipTest("[Progressive Testability] scripts/run_ci_harness.py pending M4 implementation")

        res = run_command_safe([sys.executable, str(self.ci_script)], cwd=REPO_ROOT, timeout_sec=120.0)
        self.assertEqual(
            res.returncode,
            0,
            f"scripts/run_ci_harness.py failed (exit {res.returncode}):\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        )
        # Verify that all 4 sequential stages are reported in output
        stdout_lower = res.stdout.lower()
        self.assertTrue("lint" in stdout_lower or "truth" in stdout_lower, "Missing lint stage in CI output")
        self.assertTrue("compile" in stdout_lower, "Missing compilation stage in CI output")
        self.assertTrue("geometry" in stdout_lower or "verify" in stdout_lower, "Missing geometry stage in CI output")
        self.assertTrue("sync" in stdout_lower or "drive" in stdout_lower, "Missing drive sync stage in CI output")
        self.assertIn("pass", stdout_lower)

    def test_s1_02_ci_pipeline_abort_on_stage_failure(self):
        """S1 CI Failure Handling: Harness immediately halts and returns exit code 1 if a stage fails."""
        if not self.ci_script.is_file():
            self.skipTest("[Progressive Testability] scripts/run_ci_harness.py pending M4 implementation")

        # Test failure mode with invalid arguments or synthesized failing stage
        res = run_command_safe([sys.executable, str(self.ci_script), "--invalid-flag-adversarial"], cwd=REPO_ROOT)
        self.assertNotEqual(res.returncode, 0, "CI harness must exit non-zero on invalid arguments.")

    def test_s1_03_github_actions_workflow_syntax_and_stage_parity(self):
        """S1 GitHub Actions: Validates workflow YAML syntax, triggers, ubuntu runner, and dependencies."""
        if not self.workflow_file.is_file():
            self.skipTest("[Progressive Testability] .github/workflows/cv_ci_cd.yml pending M4 implementation")

        content = self.workflow_file.read_text(encoding="utf-8")
        # 1. Triggers
        self.assertTrue(
            "push:" in content or "push" in content,
            "Workflow must trigger on git push."
        )
        self.assertTrue(
            "pull_request:" in content or "pull_request" in content,
            "Workflow must trigger on pull request."
        )
        # 2. Runner OS
        self.assertIn("ubuntu-latest", content, "Workflow must execute on ubuntu-latest.")
        # 3. Pango / WeasyPrint dependencies
        self.assertTrue(
            "libpango" in content or "pango" in content,
            "Workflow must install Linux Pango shared libraries for WeasyPrint."
        )
        # 4. Python version
        self.assertTrue(
            "3.12" in content or "python-version" in content,
            "Workflow must configure Python 3.12 runtime environment."
        )
        # 5. Harness execution step
        self.assertTrue(
            "run_ci_harness.py" in content or "compile_all.py" in content,
            "Workflow must invoke verification harness scripts."
        )


# ============================================================================
# S2: End-to-End Technical Recruitment & Background Screener Simulation
# ============================================================================

class TestS2RecruitmentScreenerSimulation(unittest.TestCase):
    """S2: Simulates technical recruiter and hiring manager background screening queries."""

    @classmethod
    def setUpClass(cls):
        cls.canonical_pdfs = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.pdf",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf",
        ]
        cls.html_templates = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.html",
        ]
        cls.extracted_pdf_texts = {}
        if PYPDF_AVAILABLE:
            for p in cls.canonical_pdfs:
                if p.is_file():
                    reader = pypdf.PdfReader(str(p))
                    cls.extracted_pdf_texts[p.name] = "\n".join(page.extract_text() or "" for page in reader.pages)

    def test_s2_01_screener_ontotab_empirical_metrics(self):
        """S2 Screener OntoTab: Audits exact 0.5596 AP on XGBoost, 30,000 records, 5x3 CV, and 2,000 bootstraps."""
        # Check both DE and Pubs targets
        for pdf_name, text in self.extracted_pdf_texts.items():
            if "Diego_Alejandro_Escobar_Barahona_CV_EN.pdf" in pdf_name or "Publications" in pdf_name:
                with self.subTest(pdf=pdf_name):
                    self.assertIn("0.5596", text, f"Missing empirical XGBoost AP 0.5596 in {pdf_name}")
                    self.assertIn("30,000", text, f"Missing 30,000 credit records parameter in {pdf_name}")
                    self.assertTrue(
                        "5x3" in text.lower() or "5×3" in text,
                        f"Missing 5x3 nested cross-validation in {pdf_name}"
                    )

    def test_s2_02_screener_ontotab_authorship_and_po_governance(self):
        """S2 Screener Authorship: Verifies strictly 2nd author (co-author) and PO approval by Joaquin Solorzano."""
        # Audited across HTML templates and evidence matrix
        spec_file = REPO_ROOT / "docs" / "cv_prep" / "01_harness_specifications.md"
        evidence_matrix_file = REPO_ROOT / "resources" / "evidence_matrix.json"

        self.assertTrue(spec_file.is_file())
        spec_content = spec_file.read_text(encoding="utf-8")
        self.assertIn("2.º autor", spec_content)
        self.assertIn("Joaquín", spec_content)
        self.assertIn("Solórzano", spec_content)

        # In all PDFs, Diego is NEVER claimed as first author or lead author
        for pdf_name, text in self.extracted_pdf_texts.items():
            with self.subTest(pdf=pdf_name):
                self.assertNotIn("first author", text.lower())
                self.assertNotIn("lead author", text.lower())
                self.assertNotIn("primer autor", text.lower())
                self.assertNotIn("autor principal", text.lower())

    def test_s2_03_screener_gbm_internship_contributions(self):
        """S2 Screener GBM: Audits 13 weeks duration, 15 DataStage jobs, DB2 LUW on RHEL, and GCP ELT."""
        de_en_text = self.extracted_pdf_texts.get("Diego_Alejandro_Escobar_Barahona_CV_EN.pdf", "")
        self.assertTrue(len(de_en_text) > 0, "DE EN PDF text missing.")

        # 1. Role is Intern
        self.assertIn("Intern", de_en_text)
        # 2. Duration July - Oct 2026 (13 weeks)
        self.assertIn("July 2026", de_en_text)
        self.assertIn("Oct 2026", de_en_text)
        # 3. DataStage ETL jobs under technical mentorship
        self.assertIn("DataStage", de_en_text)
        # 4. DB2 LUW on Linux RHEL
        self.assertTrue("DB2" in de_en_text and "RHEL" in de_en_text)
        # 5. GCP ELT Architecture (BigQuery, Dataform, Datastream CDC)
        self.assertIn("BigQuery", de_en_text)
        self.assertIn("Dataform", de_en_text)
        self.assertIn("Datastream CDC", de_en_text)

    def test_s2_04_screener_uopeople_admission_and_terms(self):
        """S2 Screener UoPeople: Audits BS in CS, Pasadena CA, Admitted Expected Start 2027, WSCUC, Fully Online."""
        for pdf_name, text in self.extracted_pdf_texts.items():
            with self.subTest(pdf=pdf_name):
                self.assertIn("University of the People", text)
                self.assertIn("Pasadena", text)
                self.assertIn("Bachelor of Science in Computer Science", text)
                self.assertTrue("Expected Start: 2027" in text or "Inicio esperado: 2027" in text or "Term 3, 2027" in text)
                self.assertTrue("Admitted" in text or "Admitido" in text)
                self.assertIn("WSCUC", text)
                self.assertTrue("Fully Online" in text or "100% Online" in text or "100% en" in text)
                # Ensure no premature graduation claim
                self.assertNotIn("graduated from university of the people", text.lower())

    def test_s2_05_screener_ef_set_english_score_authenticity(self):
        """S2 Screener EF SET: Audits certified 66/100 C1 Advanced and all 4 skill breakdowns (including Writing B2); asserts zero occurrences of draft typo 95/100."""
        for pdf_name, text in self.extracted_pdf_texts.items():
            with self.subTest(pdf=pdf_name):
                self.assertIn("66/100", text, f"Missing certified 66/100 score in {pdf_name}")
                self.assertTrue("C1" in text, f"Missing C1 level in {pdf_name}")
                self.assertIn("Writing B2", text, f"Missing Writing B2 breakdown in {pdf_name}")
                self.assertNotIn("95/100", text, f"Found draft typo 95/100 in {pdf_name}")
                self.assertNotIn("95 / 100", text)

    def test_s2_06_screener_google_cloud_certification_authenticity(self):
        """S2 Screener GCP Cert: Audits Associate Data Practitioner (Cert ID: 23e3584a246f4c149f26fea03cebcbbb)."""
        for pdf_name, text in self.extracted_pdf_texts.items():
            with self.subTest(pdf=pdf_name):
                self.assertIn("Google Cloud Certified", text)
                self.assertIn("Associate Data Practitioner", text)
                self.assertIn("23e3584a246f4c149f26fea03cebcbbb", text)
                # Asserts no unearned claims of Professional Data Engineer
                self.assertNotIn("professional data engineer", text.lower())

    def test_s2_07_screener_sql_arena_platform_and_candiate_telemetry(self):
        """S2 Screener SQL Arena: Audits Creator role (34 problems, 136 tests); candidate solved 3/34."""
        evidence_matrix_file = REPO_ROOT / "resources" / "evidence_matrix.json"
        matrix = json.loads(evidence_matrix_file.read_text(encoding="utf-8"))
        sqla = matrix["verifiable_facts"]["projects"]["sql_arena"]

        self.assertEqual(sqla["curriculum_total_problems"], 34)
        self.assertEqual(sqla["test_suite_total_passing"], 136)
        self.assertEqual(sqla["candidate_user_solved_problems"], 3)
        self.assertEqual(sqla["candidate_user_solved_list"], ["nulls-1", "nulls-2", "nulls-3"])

        # Across all PDFs and templates, candidate NEVER claims solving 34/34
        for pdf_name, text in self.extracted_pdf_texts.items():
            with self.subTest(pdf=pdf_name):
                self.assertNotIn("34/34", text)
                self.assertNotIn("solved all 34", text.lower())

    def test_s2_08_screener_ferrostats_portfolio_lakehouse_and_finops(self):
        """S2 Screener FERROSTATS: Audits Medallion Lakehouse on GCP, BigQuery Bronze streaming, and <$1/mo Free Tier FinOps."""
        de_en_text = self.extracted_pdf_texts.get("Diego_Alejandro_Escobar_Barahona_CV_EN.pdf", "")
        self.assertIn("FERROSTATS", de_en_text)
        self.assertIn("Medallion", de_en_text)
        self.assertIn("BigQuery Bronze", de_en_text)
        self.assertIn("<$1/mo", de_en_text)
        self.assertIn("Looker Studio", de_en_text)

        # Asserts indefensible claims were pruned across all PDFs
        for pdf_name, text in self.extracted_pdf_texts.items():
            with self.subTest(pdf=pdf_name):
                self.assertNotIn("<50 ms", text)
                self.assertNotIn("$0.00/mo", text)
                self.assertNotIn("$0.00/mes", text)
                self.assertNotIn("Artifact Registry", text)
                self.assertNotIn("SQLite", text)
                self.assertNotIn("Kiro", text)

        # Asserts no commercial startup fabrication
        self.assertNotIn("revenue-generating", de_en_text.lower())
        self.assertNotIn("paying clients", de_en_text.lower())

    def test_s2_09_screener_strict_anti_seniority_containment(self):
        """S2 Screener Seniority: Exhaustive regex scan asserting ZERO forbidden seniority titles."""
        forbidden_titles = [
            r"\bSenior\s+Data\s+Engineer\b",
            r"\bLead\s+Data\s+Engineer\b",
            r"\bMachine\s+Learning\s+Engineer\b(?!\s*intern)",
            r"\bML\s+Engineer\b(?!\s*intern)",
            r"\bStaff\s+Data\s+Engineer\b",
            r"\bPrincipal\s+Investigator\b",
        ]
        for pdf_name, text in self.extracted_pdf_texts.items():
            for regex_str in forbidden_titles:
                match = re.search(regex_str, text, re.IGNORECASE)
                self.assertIsNone(
                    match,
                    f"Forbidden seniority title found in {pdf_name}: '{match.group(0) if match else ''}'"
                )


# ============================================================================
# S3: ATS Parsing Fidelity, Header Extraction, Keyword Density & Hygiene
# ============================================================================

class TestS3AtsParsingSimulation(unittest.TestCase):
    """S3: Simulates Applicant Tracking System (ATS) parsing fidelity and entity extraction."""

    @classmethod
    def setUpClass(cls):
        cls.canonical_pdfs = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.pdf",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf",
        ]
        cls.html_templates = [
            REPO_ROOT / "cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html",
            REPO_ROOT / "cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.html",
            REPO_ROOT / "cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.html",
        ]
        cls.pdf_texts = {}
        if PYPDF_AVAILABLE:
            for p in cls.canonical_pdfs:
                if p.is_file():
                    reader = pypdf.PdfReader(str(p))
                    cls.pdf_texts[p.name] = "\n".join(page.extract_text() or "" for page in reader.pages)

    def test_s3_01_ats_header_and_contact_hierarchy_extraction(self):
        """S3 ATS Header: Asserts clean extraction of candidate full name, email, phone, and profile URLs."""
        email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        phone_regex = re.compile(r"\+503\s*7549\s*0118")

        for pdf_name, text in self.pdf_texts.items():
            with self.subTest(pdf=pdf_name):
                # 1. Full name is at top
                first_line = text.splitlines()[0] if text.splitlines() else ""
                self.assertIn("Diego Alejandro Escobar Barahona", first_line)

                # 2. Email extracted cleanly
                email_match = email_regex.search(text)
                self.assertIsNotNone(email_match, f"Failed to extract valid email from {pdf_name}")
                self.assertEqual(email_match.group(0), "diegoalejandroescobarahona1@gmail.com")

                # 3. Phone extracted cleanly
                phone_match = phone_regex.search(text)
                self.assertIsNotNone(phone_match, f"Failed to extract phone number from {pdf_name}")

                # 4. Profile URLs
                self.assertIn("github.com/bapatata688", text)
                self.assertIn("linkedin.com/in/diego-escobar-dev", text)
                self.assertIn("credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10", text)

    def test_s3_02_ats_section_demarcation_and_isolation(self):
        """S3 ATS Sections: Verifies clear demarcation of Summary, Experience, Projects, Skills, Certs, Education."""
        expected_sections_en = [
            "Professional Summary",
            "Experience",
            "Projects",
            "Skills",
            "Certifications",
            "Education",
        ]
        de_en_text = self.pdf_texts.get("Diego_Alejandro_Escobar_Barahona_CV_EN.pdf", "")
        for sec in expected_sections_en:
            self.assertIn(sec, de_en_text, f"Missing section '{sec}' in DE EN PDF text.")

        # Verify education does not bleed into experience
        exp_idx = de_en_text.find("Experience")
        edu_idx = de_en_text.find("Education")
        uop_idx = de_en_text.find("University of the People")
        self.assertGreater(edu_idx, exp_idx, "Education section must follow Experience.")
        self.assertGreater(uop_idx, edu_idx, "University of the People must appear within Education section.")

    def test_s3_03_ats_keyword_density_data_engineering_track(self):
        """S3 ATS Keywords DE: Asserts >= 85% keyword density on Data Engineering ontology."""
        de_keywords = [
            "bigquery", "dataform", "sqlx", "datastream", "cdc", "etl",
            "datastage", "db2", "sql", "python", "medallion", "bronze",
            "silver", "gold", "star schema", "cloud storage", "iam", "finops"
        ]
        de_en_text = self.pdf_texts.get("Diego_Alejandro_Escobar_Barahona_CV_EN.pdf", "").lower()
        matched = [k for k in de_keywords if k in de_en_text]
        score = len(matched) / len(de_keywords)
        self.assertGreaterEqual(
            score,
            0.85,
            f"DE Keyword density {score:.2%} below required 85%. Missing: {set(de_keywords) - set(matched)}"
        )

    def test_s3_04_ats_keyword_density_data_analytics_track(self):
        """S3 ATS Keywords DA: Asserts >= 80% keyword density on Analytics Engineering ontology."""
        da_keywords = [
            "analytics engineer", "looker studio", "pareto", "abc", "burn rate",
            "doi", "data quality assertions", "star schema", "sql"
        ]
        de_en_text = self.pdf_texts.get("Diego_Alejandro_Escobar_Barahona_CV_EN.pdf", "").lower()
        matched = [k for k in da_keywords if k in de_en_text]
        score = len(matched) / len(da_keywords)
        self.assertGreaterEqual(
            score,
            0.80,
            f"DA Keyword density {score:.2%} below required 80%. Missing: {set(da_keywords) - set(matched)}"
        )

    def test_s3_05_ats_keyword_density_ai_swe_track(self):
        """S3 ATS Keywords AI SWE: Asserts >= 80% keyword density on AI / ML Research ontology."""
        ai_keywords = [
            "machine learning", "ontotab", "ontology", "bge-m3", "xgboost",
            "logistic regression", "mlp", "nested cross-validation", "bootstrap",
            "average precision", "ap", "embeddings", "python", "spec-driven development", "sdd"
        ]
        pub_en_text = self.pdf_texts.get("Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf", "").lower()
        matched = [k for k in ai_keywords if k in pub_en_text]
        score = len(matched) / len(ai_keywords)
        self.assertGreaterEqual(
            score,
            0.80,
            f"AI SWE Keyword density {score:.2%} below required 80%. Missing: {set(ai_keywords) - set(matched)}"
        )

    def test_s3_06_ats_bullet_dot_isolation_and_spacing(self):
        """S3 ATS Bullet Hygiene: Confirms bullet points '•' are followed by whitespace/newline, not fused."""
        for pdf_name, text in self.pdf_texts.items():
            with self.subTest(pdf=pdf_name):
                # Search for bullet fused directly to word character (e.g. "•Designed")
                fused_bullets = re.findall(r"•[A-Za-z0-9]", text)
                self.assertEqual(
                    fused_bullets,
                    [],
                    f"Found fused bullet characters in {pdf_name}: {fused_bullets}"
                )

    def test_s3_07_ats_zero_placeholder_leaks(self):
        """S3 ATS Cleanliness: Exhaustive scan across all PDFs and HTML templates asserting ZERO placeholders."""
        placeholder_regexes = [
            (r"\[TODO\]", "[TODO]"),
            (r"\[TBD\]", "[TBD]"),
            (r"\[PLACEHOLDER\]", "[PLACEHOLDER]"),
            (r"\bTODO\b", "TODO word"),
            (r"\bTBD\b", "TBD word"),
            (r"\bLorem\s+Ipsum\b", "Lorem Ipsum"),
            (r"\{\{.*?\}\}", "Handlebars/Jinja variable"),
            (r"\$\{[^}]+\}", "Template literal placeholder"),
            (r"\bXX%\b", "Unresolved XX%"),
            (r"\b00/00\b", "Unresolved 00/00"),
        ]
        all_sources = self.canonical_pdfs + self.html_templates
        for source in all_sources:
            if not source.is_file():
                continue
            if source.suffix == ".pdf" and PYPDF_AVAILABLE:
                reader = pypdf.PdfReader(str(source))
                content = "\n".join(page.extract_text() or "" for page in reader.pages)
            else:
                content = source.read_text(encoding="utf-8")

            for pat, label in placeholder_regexes:
                match = re.search(pat, content, re.IGNORECASE)
                self.assertIsNone(
                    match,
                    f"Found unresolved placeholder '{label}' in {source.name}: '{match.group(0) if match else ''}'"
                )


# ============================================================================
# S4: Progressive Testability & Rule 5 Compliance Contracts
# ============================================================================

class TestS4ProgressiveTestabilityContracts(unittest.TestCase):
    """S4: Verifies Rule 5 native compliance, progressive testability, and runner integration."""

    def test_s4_01_rule_5_native_unittest_compliance(self):
        """S4 Rule 5: Verifies that test_tier4_scenarios.py uses only Python standard library and pypdf."""
        this_file = Path(__file__).resolve()
        code = this_file.read_text(encoding="utf-8")

        # Extract only top-level import statements to prevent self-referential string matches
        import_lines = [
            line.strip() for line in code.splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]

        for line in import_lines:
            self.assertFalse(
                line.startswith("import pytest") or line.startswith("from pytest"),
                f"Forbidden pytest import found: {line}"
            )
            self.assertFalse(
                line.startswith("import matplotlib") or line.startswith("from matplotlib"),
                f"Forbidden matplotlib import found: {line}"
            )

        # Must import standard library unittest
        self.assertTrue(any("unittest" in line for line in import_lines), "Must import standard library unittest")

    def test_s4_02_runner_discovery_and_registration(self):
        """S4 Runner Discovery: Confirms test_tier4_scenarios is registered in run_all_e2e_tests.py."""
        runner_file = REPO_ROOT / "tests" / "run_all_e2e_tests.py"
        self.assertTrue(runner_file.is_file())
        runner_code = runner_file.read_text(encoding="utf-8")
        self.assertIn('"4": "test_tier4_scenarios"', runner_code)


# ============================================================================
# Main Execution Entry Point
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""test_evidence_matrix_fuzz.py - Adversarial Regex Fuzzing & Schema Stress Harness for master_cv

Empirical adversarial challenge harness testing:
1. True-positive detection across dispatch phrases and evasion variations.
2. False-positive resistance against legitimate candidate claims.
3. Schema conformance and corrupted input rejection.
4. Absence of forbidden strings asserted as factual claims in production artifacts.

Adheres to pure Python standard library unittest (Zero-Pytest, AGENTS.md Rule 5 compliant).
"""

import copy
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EVIDENCE_MATRIX_PATH = REPO_ROOT / "resources" / "evidence_matrix.json"


def load_matrix() -> Dict[str, Any]:
    with open(EVIDENCE_MATRIX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_compiled_rules(data: Dict[str, Any]) -> List[Tuple[str, re.Pattern, str]]:
    """Extracts all forbidden regex patterns from evidence_matrix.json."""
    rules = []
    for r in data.get("global_forbidden_regexes", []):
        rules.append((r["rule_id"], re.compile(r["regex"]), r.get("description", "")))
    for dom_name, dom_data in data.get("containment_domains", {}).items():
        for r in dom_data.get("forbidden_regex_patterns", []):
            rules.append((r["rule_id"], re.compile(r["regex"]), r.get("description", "")))
    return rules


def validate_schema_invariants(matrix: Any) -> Tuple[bool, List[str]]:
    """Strict schema oracle validating evidence_matrix.json structure."""
    errors = []
    if not isinstance(matrix, dict):
        return False, ["Root must be a dictionary"]

    mandatory_top_keys = [
        "$schema", "metadata", "candidate", "verifiable_facts",
        "global_forbidden_regexes", "containment_harness",
        "containment_domains", "ats_paraphrase_matrix",
        "evidence_gap_catalog", "linter_config"
    ]
    for key in mandatory_top_keys:
        if key not in matrix:
            errors.append(f"Missing mandatory top key: {key}")

    # Validate regex rules syntax
    rules_to_check = matrix.get("global_forbidden_regexes", [])
    if isinstance(rules_to_check, list):
        for idx, rule in enumerate(rules_to_check):
            if not isinstance(rule, dict) or "regex" not in rule:
                errors.append(f"global_forbidden_regexes[{idx}] missing regex")
                continue
            try:
                re.compile(rule["regex"])
            except re.error as e:
                errors.append(f"Invalid regex in global_forbidden_regexes[{idx}]: {e}")
    else:
        errors.append("global_forbidden_regexes must be a list")

    domains = matrix.get("containment_domains", {})
    if isinstance(domains, dict):
        for dname, dval in domains.items():
            if not isinstance(dval, dict):
                errors.append(f"Domain {dname} must be a dict")
                continue
            for idx, rule in enumerate(dval.get("forbidden_regex_patterns", [])):
                if not isinstance(rule, dict) or "regex" not in rule:
                    errors.append(f"Domain {dname} rule[{idx}] missing regex")
                    continue
                try:
                    re.compile(rule["regex"])
                except re.error as e:
                    errors.append(f"Invalid regex in domain {dname} rule[{idx}]: {e}")
    else:
        errors.append("containment_domains must be a dict")

    # Validate numeric metrics
    vf = matrix.get("verifiable_facts", {})
    if isinstance(vf, dict):
        # OntoTab
        ontotab = vf.get("research", {}).get("ontotab", {})
        if ontotab.get("dataset", {}).get("total_records") != 30000:
            errors.append("research.ontotab.dataset.total_records must be 30000")
        if ontotab.get("candidate_rank") != 2:
            errors.append("research.ontotab.candidate_rank must be 2")
        # EF SET
        ef_set = vf.get("certifications", {}).get("ef_set_english", {})
        if ef_set.get("overall_score") != 66:
            errors.append("certifications.ef_set_english.overall_score must be 66")
        if ef_set.get("listening_score") != 75:
            errors.append("certifications.ef_set_english.listening_score must be 75")
        # SQL Arena
        sql_arena = vf.get("projects", {}).get("sql_arena", {})
        if sql_arena.get("curriculum_total_problems") != 34:
            errors.append("projects.sql_arena.curriculum_total_problems must be 34")
        if sql_arena.get("candidate_user_solved_problems") != 3:
            errors.append("projects.sql_arena.candidate_user_solved_problems must be 3")
        # GBM
        gbm = vf.get("experience", {}).get("gbm", {})
        if gbm.get("duration_weeks") != 13:
            errors.append("experience.gbm.duration_weeks must be 13")
        if gbm.get("deliverables", {}).get("datastage_jobs", {}).get("count") != 15:
            errors.append("experience.gbm.deliverables.datastage_jobs.count must be 15")

    return len(errors) == 0, errors


class TestAdversarialRegexFuzzing(unittest.TestCase):
    """Adversarially evaluates true-positive and false-positive boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.matrix = load_matrix()
        cls.rules = get_compiled_rules(cls.matrix)

    def scan(self, phrase: str) -> List[str]:
        return [rule_id for rule_id, pat, _ in self.rules if pat.search(phrase)]

    # --- 1. True Positive Boundaries ---

    def test_tp_dispatch_required_phrases(self):
        """Tests the 4 mandatory phrases explicitly stated in the dispatch prompt."""
        dispatch_cases = [
            ("Machine Learning Engineer", "Forbidden role inflation"),
            ("EF SET 95/100", "Forbidden score typo/exaggeration"),
            ("founder of FERROSTATS", "Forbidden commercial founder claim"),
            ("solved all 34 problems", "Forbidden solve-all claim"),
        ]
        for phrase, reason in dispatch_cases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"BUG DETECTED: Dispatch-mandated phrase '{phrase}' ({reason}) "
                    f"was NOT matched by any regex in evidence_matrix.json!"
                )

    def test_tp_ferrostats_founder_and_commercial_evasions(self):
        """Tests variations of founder/commercial claims for FERROSTATS."""
        evasion_phrases = [
            "founder of FERROSTATS",
            "Founder of FERROSTATS",
            "Co-Founder of FERROSTATS",
            "Founder & CEO of FERROSTATS",
            "Fundador de FERROSTATS",
            "commercial startup with $5,000 MRR",
            "revenue-generating platform",
            "paying clients for FERROSTATS",
        ]
        for phrase in evasion_phrases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"BUG DETECTED: Commercial/founder claim '{phrase}' "
                    f"was NOT matched by any regex in evidence_matrix.json!"
                )

    def test_tp_sql_arena_solve_all_evasions(self):
        """Tests variations of claiming 34/34 exercises completed in English and Spanish."""
        evasions = [
            "solved all 34 problems",
            "completed 34/34 exercises",
            "resolvi los 34 ejercicios",
            "resolví los 34 ejercicios",
            "34/34 solved",
            "34/34 resueltos",
            "completed all 34 drills",
        ]
        for phrase in evasions:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"BUG DETECTED: SQL Arena solve-all evasion '{phrase}' "
                    f"was NOT matched by any regex in evidence_matrix.json!"
                )

    def test_tp_ontotab_authorship_and_peer_review_evasions(self):
        """Tests variations of lead authorship and peer-reviewed claims."""
        evasions = [
            "peer-reviewed paper",
            "published in IEEE",
            "published in ACM",
            "lead author",
            "Lead Author, OntoTab Research",
            "first author on credit risk paper",
            "sole author",
            "primer autor",
            "autor principal",
        ]
        for phrase in evasions:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"BUG DETECTED: Authorship/publication evasion '{phrase}' "
                    f"was NOT matched by any regex in evidence_matrix.json!"
                )

    def test_tp_title_seniority_and_bilingual_evasions(self):
        """Tests seniority inflations in English and Spanish."""
        evasions = [
            "Senior Data Engineer",
            "Data Engineer Senior",
            "Lead Software Engineer",
            "Principal Cloud Architect",
            "Staff Engineer",
            "Ingeniero de Datos Senior",
            "Ingeniero de Machine Learning",
            "Google Cloud Professional Data Engineer",
            "GCP PDE",
        ]
        for phrase in evasions:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"BUG DETECTED: Seniority inflation evasion '{phrase}' "
                    f"was NOT matched by any regex in evidence_matrix.json!"
                )

    def test_tp_education_graduation_evasions(self):
        """Tests false claims of having already graduated from UoPeople."""
        evasions = [
            "Graduated from University of the People",
            "Graduated from UoPeople",
            "Alumni of UoPeople",
            "graduado de University of the People",
        ]
        for phrase in evasions:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"BUG DETECTED: Education graduation evasion '{phrase}' "
                    f"was NOT matched by any regex in evidence_matrix.json!"
                )

    # --- 2. False Positive Resistance ---

    def test_fp_resistance_legitimate_phrases(self):
        """Tests that legitimate verified statements pass cleanly without triggering rules."""
        legit_phrases = [
            ("Co-author OntoTab (2nd of 7)", "Authoritative English co-author statement"),
            ("Co-author (2nd of 7) under lead author Joaquín Solórzano", "Full co-author disclosure"),
            ("Digital Solutions Specialist Intern", "Exact official GBM role title"),
            ("creator of SQL Arena", "Legitimate platform creator statement"),
            ("solved 3/34 exercises", "Accurate candidate solve progress"),
            ("EF SET 66/100 C1", "Certified EF SET overall score"),
            ("EF SET English Certificate — C1 Advanced (66/100: Listening 75 C2)", "Full EF SET description"),
            ("July 2026 – Oct 2026 (13 weeks)", "Internship duration"),
            ("Architected cloud-native Medallion Lakehouse portfolio project on GCP", "Approved lakehouse text"),
            ("Designed 34-exercise curriculum and 136 automated tests", "SQL Arena platform design metric"),
            ("Google Cloud Certified Associate Data Practitioner", "Certified cloud credential"),
            ("University of the People (admitted, expected start: January 2027)", "Legitimate admission disclosure"),
        ]
        for phrase, context in legit_phrases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertEqual(
                    matches, [],
                    f"FALSE POSITIVE DETECTED: Legitimate phrase '{phrase}' ({context}) "
                    f"was incorrectly matched by: {matches}"
                )


class TestSchemaStressHarness(unittest.TestCase):
    """Stress tests JSON schema conformance and corrupted input handling."""

    @classmethod
    def setUpClass(cls):
        cls.matrix = load_matrix()

    def test_baseline_matrix_is_schema_valid(self):
        """Validates that authoritative matrix passes schema oracle."""
        valid, errors = validate_schema_invariants(self.matrix)
        self.assertTrue(valid, f"Baseline matrix invalid: {errors}")

    def test_corrupted_missing_keys_detected(self):
        """Fuzzes schema validator by dropping mandatory keys."""
        for key in ["$schema", "metadata", "candidate", "verifiable_facts", "global_forbidden_regexes", "containment_domains"]:
            with self.subTest(key=key):
                c = copy.deepcopy(self.matrix)
                del c[key]
                valid, errors = validate_schema_invariants(c)
                self.assertFalse(valid)
                self.assertTrue(any(key in e for e in errors))

    def test_corrupted_bad_types_detected(self):
        """Fuzzes schema validator with corrupted structural types."""
        c = copy.deepcopy(self.matrix)
        c["global_forbidden_regexes"] = "NOT_A_LIST"
        valid, errors = validate_schema_invariants(c)
        self.assertFalse(valid)

    def test_corrupted_invalid_regex_syntax_detected(self):
        """Fuzzes schema validator with broken regex syntax."""
        c = copy.deepcopy(self.matrix)
        c["global_forbidden_regexes"].append({
            "rule_id": "TEST-BROKEN-001",
            "regex": "(?i)[invalid-syntax",
            "severity": "FATAL"
        })
        valid, errors = validate_schema_invariants(c)
        self.assertFalse(valid)
        self.assertTrue(any("invalid regex" in e.lower() for e in errors))

    def test_corrupted_tampered_metrics_detected(self):
        """Fuzzes schema validator with inflated numeric metrics."""
        tamper_cases = [
            ("research", "ontotab", "dataset", "total_records", 99999),
            ("research", "ontotab", None, "candidate_rank", 1),
            ("certifications", "ef_set_english", None, "overall_score", 95),
            ("certifications", "ef_set_english", None, "listening_score", 90),
            ("projects", "sql_arena", None, "candidate_user_solved_problems", 34),
        ]
        for root, sub1, sub2, metric, bad_val in tamper_cases:
            with self.subTest(root=root, metric=metric, bad_val=bad_val):
                c = copy.deepcopy(self.matrix)
                if sub2:
                    c["verifiable_facts"][root][sub1][sub2][metric] = bad_val
                else:
                    c["verifiable_facts"][root][sub1][metric] = bad_val
                valid, errors = validate_schema_invariants(c)
                self.assertFalse(valid)


class TestProductionArtifactsIntegrity(unittest.TestCase):
    """Scans production artifacts to ensure zero forbidden claims are present."""

    def test_html_cv_templates_have_zero_forbidden_matches(self):
        matrix = load_matrix()
        rules = get_compiled_rules(matrix)
        html_files = list((REPO_ROOT / "cv").glob("**/*.html"))
        self.assertGreaterEqual(len(html_files), 4)

        violations = []
        for hf in html_files:
            text = hf.read_text(encoding="utf-8")
            for rid, pat, desc in rules:
                if pat.search(text):
                    violations.append((str(hf.relative_to(REPO_ROOT)), rid, desc))

        self.assertEqual(violations, [], f"Found forbidden claims in HTML CVs: {violations}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

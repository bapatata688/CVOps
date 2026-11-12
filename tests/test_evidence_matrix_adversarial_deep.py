#!/usr/bin/env python3
"""test_evidence_matrix_adversarial_deep.py - Novel Adversarial Attack Vectors and Stress Harness

Empirically challenges resources/evidence_matrix.json against novel evasions:
- Casing variations (ALL CAPS, MiXeD CaSe)
- Accented Unicode characters (á, é, í, ó, ú)
- Unusual whitespace (tabs, multiple spaces, newlines)
- Punctuation (hyphens, slashes, ampersands, colons, dollar signs)
- Bilingual evasive phrasings across 6 domains:
  1. OntoTab Authorship & Peer Review (e.g. Lead Author, Investigador Principal)
  2. FERROSTATS Commercial / Founder Claims (e.g. $5,000 MRR, $50,000 ARR, revenue, founder, ceo)
  3. SQL Arena 34/34 Solve Claims (e.g. 34 out of 34 solved, 34 de 34 resueltos)
  4. Job Title Seniority Inflations (e.g. Data Engineer Staff, Sr. Data Engineer, Ingeniero de Datos Staff)
  5. UoPeople Graduation Claims (e.g. graduate of UoPeople, egresado de University of the People)
  6. EF SET Score Inflations (e.g. EF SET: 95, EF SET - 95, 95/100)
- False-Positive Resistance against legitimate candidate claims and official facts.

Strict standard-library unittest (Zero-Pytest, AGENTS.md Rule 5 compliant).
"""

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


def get_all_rules(matrix: Dict[str, Any]) -> List[Tuple[str, re.Pattern, str]]:
    """Gathers all rules: global, domain-specific, and containment harness patterns."""
    rules = []
    # 1. Global forbidden regexes
    for r in matrix.get("global_forbidden_regexes", []):
        rules.append((r["rule_id"], re.compile(r["regex"]), r.get("description", "")))
    # 2. Domain forbidden regexes
    for dom_name, dom_data in matrix.get("containment_domains", {}).items():
        for r in dom_data.get("forbidden_regex_patterns", []):
            rules.append((r["rule_id"], re.compile(r["regex"]), r.get("description", "")))
    # 3. Containment harness patterns
    for idx, h in enumerate(matrix.get("containment_harness", {}).get("forbidden_regex_patterns", [])):
        rules.append((f"HARNESS-PATTERN-{idx+1}", re.compile(h["pattern"]), h.get("reason", "")))
    return rules


class TestNovelAdversarialAttacks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = load_matrix()
        cls.rules = get_all_rules(cls.matrix)

    def scan(self, phrase: str) -> List[str]:
        return [rule_id for rule_id, pat, _ in self.rules if pat.search(phrase)]

    # =========================================================================
    # 1. OntoTab Authorship & Peer-Review Claims
    # =========================================================================
    def test_novel_ontotab_authorship_and_peer_review_evasions(self):
        cases = [
            # Casing & title-case variations
            "LEAD AUTHOR",
            "Lead Author",
            "lead author",
            "lEaD aUtHoR",
            "Lead Researcher",
            "lead scientist",
            "Principal Investigator",
            "Investigador Principal",
            "investigador principal",
            "Investigador Principal en OntoTab",
            "FIRST AUTHOR",
            "First Author",
            "sole author",
            "SOLE AUTHOR",
            "PRIMER AUTOR",
            "primer autor",
            "AUTOR PRINCIPAL",
            "autor principal",
            "AUTOR ÚNICO",
            "autor único",
            "autor unico",
            # Whitespace & punctuation variations
            "lead   author",
            "lead\tauthor",
            "lead\nauthor",
            "primer   autor",
            "primer\tautor",
            "autor   principal",
            "autor\tprincipal",
            # Peer review and venue evasions
            "PEER-REVIEWED",
            "peer-reviewed",
            "Peer-Reviewed",
            "peer-reviewed paper",
            "peer-reviewed conference publication",
            "published in IEEE",
            "PUBLISHED IN IEEE",
            "published in ACM",
            "published in NeurIPS",
            "published in ICML",
            "published in CVPR",
            "published in KDD",
            "publicado en IEEE",
            "PUBLICADO EN NEURIPS",
            "publicado en cvpr",
            "publicado en ICML",
            "revisado por pares",
            "REVISADO POR PARES",
            "artículo revisado por pares",
            "indexed journal",
            "revista indexada",
            "REVISTA INDEXADA",
            "formalmente publicado",
            "FORMALMENTE PUBLICADO",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"OntoTab evasion NOT caught: '{phrase}'"
                )

    # =========================================================================
    # 2. FERROSTATS Commercial / Founder Claims
    # =========================================================================
    def test_novel_ferrostats_commercial_and_founder_evasions(self):
        cases = [
            # Founder / C-level variations
            "founder of FERROSTATS",
            "Founder of FERROSTATS",
            "FOUNDER OF FERROSTATS",
            "Co-Founder of FERROSTATS",
            "co-founder of FERROSTATS",
            "Co-founder of FERROSTATS",
            "CO-FOUNDER",
            "cofounder of FERROSTATS",
            "Cofounder",
            "COFOUNDER",
            "Founder & CEO",
            "CEO of FERROSTATS",
            "ceo of FERROSTATS",
            "Fundador de FERROSTATS",
            "fundador de FERROSTATS",
            "FUNDADOR",
            "Co-Fundador de FERROSTATS",
            "co-fundador",
            "co-fundador de FERROSTATS",
            "cofundador de FERROSTATS",
            # Commercial & Revenue claims
            "commercial startup",
            "COMMERCIAL STARTUP",
            "startup with paying customers",
            "paying client",
            "paying clients",
            "PAYING CLIENTS",
            "paying customers",
            "revenue-generating platform",
            "REVENUE-GENERATING",
            "$5,000 MRR",
            "$10,000 mrr",
            "$50,000 ARR",
            "$100,000 arr",
            "$250,000 revenue",
            "raised $500k",
            "empresa comercial",
            "EMPRESA COMERCIAL",
            "clientes de pago",
            "CLIENTES DE PAGO",
            # Distributed cluster claim
            "production pyspark cluster",
            "PRODUCTION PYSPARK CLUSTER",
            "distributed spark cluster in prod",
            "cluster pyspark en produccion",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"FERROSTATS evasion NOT caught: '{phrase}'"
                )

    # =========================================================================
    # 3. SQL Arena 34/34 Solve Claims
    # =========================================================================
    def test_novel_sql_arena_solve_all_evasions(self):
        cases = [
            # English verbs & forms
            "solved all 34 problems",
            "SOLVED ALL 34 PROBLEMS",
            "solved all 34 exercises",
            "solved 34 exercises",
            "completed all 34 problems",
            "completed 34/34 exercises",
            "completed all 34 drills",
            "completed 34 drills",
            # English trailing / ratio format
            "34/34 solved",
            "34 / 34 solved",
            "34/34 SOLVED",
            "34/34 completed",
            "34 / 34 completed",
            "34 out of 34 solved",
            "34 of 34 solved",
            # Spanish verbs & accents
            "resolví los 34 ejercicios",
            "RESOLVÍ LOS 34 EJERCICIOS",
            "resolvi los 34 ejercicios",
            "resolví todos los 34 ejercicios",
            "resolvi todos los 34 problemas",
            "resolví 34 problemas",
            "resolvi 34 retos",
            "completé los 34 ejercicios",
            "complete los 34 ejercicios",
            "completó todos los 34 problemas",
            "completo todos los 34 problemas",
            # Spanish trailing / ratio format
            "34/34 resueltos",
            "34 / 34 resueltos",
            "34/34 RESUELTOS",
            "34/34 resuelto",
            "34 / 34 resuelto",
            "34/34 completados",
            "34 / 34 completados",
            "34/34 completado",
            "34 de 34 resueltos",
            # SaaS / Multi-tenant fabrications
            "thousands of users",
            "thousands of active users",
            "multi-tenant saas",
            "MULTI-TENANT SAAS",
            "miles de usuarios",
            "MILES DE USUARIOS",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"SQL Arena evasion NOT caught: '{phrase}'"
                )

    # =========================================================================
    # 4. Job Title Seniority Inflations (English & Spanish)
    # =========================================================================
    def test_novel_title_seniority_inflations(self):
        cases = [
            # Pre-fixed English titles
            "Senior Data Engineer",
            "SENIOR DATA ENGINEER",
            "Lead Data Engineer",
            "Principal Data Engineer",
            "Staff Data Engineer",
            "Senior Software Engineer",
            "Lead Cloud Architect",
            "Principal Cloud Architect",
            "Staff Software Engineer",
            "Senior AI Engineer",
            "Staff Architect",
            "Lead Scientist",
            "Principal Scientist",
            "Principal Engineer",
            "Sr. Data Engineer",
            # Post-fixed English & Spanish titles
            "Data Engineer Senior",
            "DATA ENGINEER SENIOR",
            "Data Engineer Lead",
            "Data Engineer Principal",
            "Data Engineer Staff",
            "Data Engineer Sr.",
            "Ingeniero de Datos Senior",
            "INGENIERO DE DATOS SENIOR",
            "Ingeniero de Datos Lead",
            "Ingeniero de Datos Principal",
            "Ingeniero de Datos Staff",
            "Arquitecto Cloud Senior",
            "Arquitecto Cloud Lead",
            "Arquitecto Cloud Principal",
            "Ingeniero de Software Senior",
            "ingeniero senior",
            "INGENIERO SENIOR",
            # Machine Learning Engineer (without intern)
            "Machine Learning Engineer",
            "MACHINE LEARNING ENGINEER",
            "ML Engineer",
            "ml engineer",
            "Ingeniero de Machine Learning",
            "INGENIERO DE MACHINE LEARNING",
            "Ingeniero de ML",
            "ingeniero de ml",
            "Ingeniero de Aprendizaje Automático",
            "Ingeniero de Aprendizaje Automatico",
            # Unearned Professional Certifications
            "Professional Data Engineer",
            "PROFESSIONAL DATA ENGINEER",
            "Google Cloud Professional Data Engineer",
            "Google Cloud PDE",
            "GCP PDE",
            "gcp pde",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"Title seniority evasion NOT caught: '{phrase}'"
                )

    # =========================================================================
    # 5. UoPeople Graduation Claims
    # =========================================================================
    def test_novel_uopeople_graduation_evasions(self):
        cases = [
            "Graduated from University of the People",
            "GRADUATED FROM UNIVERSITY OF THE PEOPLE",
            "graduated from UoPeople",
            "Graduated from UoPeople",
            "GRADUATED FROM UOPEOPLE",
            "degree awarded by University of the People",
            "degree awarded by UoPeople",
            "DEGREE AWARDED BY UOPEOPLE",
            "alumni of University of the People",
            "ALUMNI OF UNIVERSITY OF THE PEOPLE",
            "alumni of UoPeople",
            "Alumni of UoPeople",
            "graduate of University of the People",
            "graduate of UoPeople",
            "graduado de University of the People",
            "GRADUADO DE UNIVERSITY OF THE PEOPLE",
            "graduado de UoPeople",
            "Graduado de UoPeople",
            "titulado por University of the People",
            "titulado por UoPeople",
            "TITULADO POR UOPEOPLE",
            "egresado de University of the People",
            "egresado de UoPeople",
            # Whitespace variations
            "graduated   from   UoPeople",
            "graduado   de   UoPeople",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"UoPeople graduation evasion NOT caught: '{phrase}'"
                )

    # =========================================================================
    # 6. EF SET Score Inflations
    # =========================================================================
    def test_novel_ef_set_score_inflations(self):
        cases = [
            "EF SET 95/100",
            "certified C1/C2 English proficiency (EF SET 95/100)",
            "95/100",
            "95 / 100",
            "95   /   100",
            "95% ef set",
            "95% EF SET",
            "EF SET score of 95",
            "ef set score of 95",
            "EF SET score 95",
            "EF SET 95",
            "ef set 95",
            "EF SET: 95/100",
            "EF SET: 95",
            "EF SET - 95",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                matches = self.scan(phrase)
                self.assertGreater(
                    len(matches), 0,
                    f"EF SET score inflation NOT caught: '{phrase}'"
                )

    # =========================================================================
    # 7. False-Positive Resistance on Verified Ground Truth Facts
    # =========================================================================
    def test_false_positive_resistance_on_verified_record(self):
        legitimate_cases = [
            # OntoTab co-author legitimate statements
            ("Co-author OntoTab (2nd of 7)", "Authoritative English co-author statement"),
            ("Co-author (2nd of 7) under lead author Joaquín Solórzano", "Full co-author disclosure with lead author named"),
            ("Coautor (2.º de 7) bajo lead author Joaquín Solórzano", "Spanish co-author disclosure with lead author named"),
            ("Co-author & ML Researcher | OntoTab (GBM)", "Approved OntoTab heading"),
            ("Coautor | OntoTab (GBM): 2.º autor de 7", "Approved Spanish OntoTab heading"),
            ("Executed empirical benchmark experiments under 5×3 nested cross-validation across 30,000 public credit-risk records", "Approved OntoTab bullet"),
            ("Evaluated ontology-enriched text descriptions encoded via frozen BGE-M3 (1,024 dims)", "Approved embeddings bullet"),
            ("Baseline achieved 0.5596 AP in XGBoost (R8) versus 0.5069 AP for ontology text (R5)", "Approved metric bullet"),
            # GBM Internship legitimate statements
            ("Digital Solutions Specialist Intern (Data & AI)", "Official internship title"),
            ("Data Engineer Intern (Digital Solutions Specialist), GBM", "Approved title variant"),
            ("Junior Data Engineer | Data Engineer Intern", "Approved candidate positioning"),
            ("July 2026 – Oct 2026 (13 weeks)", "Verified internship duration"),
            ("Developed, parameterized, and tested 15 enterprise ETL jobs in IBM InfoSphere DataStage", "15 DataStage jobs deliverable"),
            ("Queried and parameterized IBM DB2 LUW on Red Hat Enterprise Linux (RHEL)", "DB2 on RHEL deliverable"),
            ("Co-designed enterprise near-real-time ELT pipeline proposal on GCP (BigQuery, Dataform SQLX, Datastream CDC)", "GCP ELT proposal deliverable"),
            ("Machine Learning Engineer Intern", "Intern qualifier on MLE"),
            ("ML Engineer Intern", "Intern qualifier on ML"),
            # FERROSTATS legitimate statements
            ("Architected cloud-native Medallion Lakehouse portfolio project on GCP", "Approved lakehouse statement"),
            ("Cloud-Native Medallion Lakehouse & ACID POS Platform on GCP", "Approved architecture statement"),
            ("Permanent $0.00/mo architecture via Cloud Run scale-to-zero (<3s cold start)", "Approved FinOps statement"),
            ("<50 ms edge latency into BigQuery Bronze via REST APIs", "Approved latency statement"),
            ("3 Gold Star Schema data marts: fct_daily_sales, mart_inventory_pareto_abc, dim_products", "Approved data marts"),
            ("3-page Looker Studio dashboard", "Approved dashboard metric"),
            ("BigQuery orchestrated via Dataform SQLX with planned batch PySpark roadmap", "Planned PySpark study roadmap"),
            # SQL Arena legitimate statements
            ("creator of SQL Arena", "Legitimate creator statement"),
            ("Full-Stack Creator & Architect of SQL Arena", "Full creator title"),
            ("Designed 34-exercise curriculum and 136 automated tests", "34 curriculum & 136 tests"),
            ("Candidate user progress: 3/34 solved", "3/34 solved progress"),
            ("solved 3/34 exercises", "Accurate 3/34 exercises"),
            ("3/34 resueltos", "Spanish 3/34 resueltos"),
            ("3 out of 34 solved", "Variant 3 out of 34"),
            ("3 de 34 resueltos", "Variant 3 de 34 resueltos"),
            ("Currently in progress on rounding-1", "Next exercise in progress"),
            ("Stack: React 19, Vite, Tailwind CSS v4, Monaco Editor, Express, MySQL 8.0", "Approved stack"),
            # EF SET English Certification legitimate statements
            ("EF SET English Certificate — C1 Advanced (66/100: Listening 75 C2)", "Full EF SET description"),
            ("EF SET 66/100 C1", "Certified score"),
            ("certified C1 Advanced English proficiency (EF SET 66/100)", "Certified summary"),
            ("Listening 75/100 C2 Proficient", "Component score listening"),
            ("Reading 67/100 C1 Advanced", "Component score reading"),
            ("Speaking 69/100 C1 Advanced", "Component score speaking"),
            ("Writing 51/100 B2 Upper Intermediate", "Component score writing"),
            # Education legitimate statements
            ("University of the People (admitted, expected start: January 2027)", "Legitimate UoPeople disclosure"),
            ("Bachelor of Science in Computer Science — University of the People (Admitted | Term 3, 2027)", "UoPeople formal block"),
            ("Bachillerato Técnico Vocacional en Desarrollo de Software (promedio acumulado 9.5 / 10.0)", "INSAL secondary education"),
            ("Graduación: 10 de diciembre de 2026", "INSAL graduation date"),
            # Certified credentials
            ("Google Cloud Certified — Associate Data Practitioner", "Certified cloud credential"),
            ("Associate Data Practitioner (Cert ID: 23e3584a246f4c149f26fea03cebcbbb)", "Full cert ID"),
        ]
        for phrase, context in legitimate_cases:
            with self.subTest(phrase=phrase, context=context):
                matches = self.scan(phrase)
                self.assertEqual(
                    matches, [],
                    f"FALSE POSITIVE DETECTED: Legitimate phrase '{phrase}' ({context}) "
                    f"was matched by: {matches}"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

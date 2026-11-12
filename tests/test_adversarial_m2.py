"""
Adversarial Verification Suite for Milestone 2 Deliverables and Google Workspace Integration.
Pure Python, zero-pytest, Rule 5 compliant.
"""
import os
import sys
import json
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

GDOCS_BIN = os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity\plugin_data\gdocs\bin\gdocs-986250228.exe")
GDRIVE_BIN = os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity\plugin_data\gdrive\bin\gdrive-1015343799.exe")

MASTER_DOC_ID = "16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ"
CV_PREP_DRIVE_FOLDER_ID = "17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb"
PORTFOLIO_ROOT_FOLDER_ID = "13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H"

DOC_HARNESS_ID = "1-DZEgwDx5rdM1gxcgYM_xMvIpM4T48wxpV-hflenKds"
DOC_PARAPHRASE_ID = "1XtA_njiDwptH1VPFV1rQ2f_VnWRn5-NHAwFaiJ80IX0"
DOC_GAPS_ID = "1kwr-QOTNp4SPmJHAVZKO2XGt6e5NQHEr9gmBKWhdfgY"

EVIDENCE_MATRIX_PATH = str(REPO_ROOT / "resources" / "evidence_matrix.json")
HARNESS_SPEC_PATH = str(REPO_ROOT / "docs" / "cv_prep" / "01_harness_specifications.md")
PARAPHRASE_PATH = str(REPO_ROOT / "docs" / "cv_prep" / "02_paraphrase_matrices.md")
GAPS_PATH = str(REPO_ROOT / "docs" / "cv_prep" / "03_evidence_gaps.md")

class TestAdversarialM2Deliverables(unittest.TestCase):

    def test_01_drive_folder_hierarchy_and_cleanliness(self):
        """Stress tests Google Drive CV_Prep folder: parent relationship, permissions, no duplicate or stray files."""
        if not os.path.isfile(GDRIVE_BIN):
            self.skipTest("gdrive CLI plugin binary not installed in this environment")
        res = subprocess.run([GDRIVE_BIN, "readonly", "info", CV_PREP_DRIVE_FOLDER_ID, "--json"], capture_output=True, text=True, check=True)
        folder_info = json.loads(res.stdout)
        self.assertEqual(folder_info.get("name"), "CV_Prep")
        self.assertEqual(folder_info.get("mimeType"), "application/vnd.google-apps.folder")
        self.assertIn(PORTFOLIO_ROOT_FOLDER_ID, folder_info.get("parents", []))

        # Check children count and exact names
        res_ls = subprocess.run([GDRIVE_BIN, "readonly", "ls", CV_PREP_DRIVE_FOLDER_ID, "--json"], capture_output=True, text=True, check=True)
        children = json.loads(res_ls.stdout)
        names = {c["name"]: c["id"] for c in children}
        
        self.assertIn(len(children), (3, 4), f"Expected 3 M2 documents (+ optional M4 calibrated folder) in CV_Prep, found {len(children)}: {names}")
        self.assertIn("01_especificaciones_y_harness", names)
        self.assertIn("02_matrices_parafrasis_ats", names)
        self.assertIn("03_auditoria_gaps_evidencia", names)
        self.assertEqual(names["01_especificaciones_y_harness"], DOC_HARNESS_ID)
        self.assertEqual(names["02_matrices_parafrasis_ats"], DOC_PARAPHRASE_ID)
        self.assertEqual(names["03_auditoria_gaps_evidencia"], DOC_GAPS_ID)

    def test_02_remote_docs_structural_and_table_integrity(self):
        """Stress tests each of the 3 remote Google Docs for content size, table existence, and auto-fitted columns."""
        if not os.path.isfile(GDOCS_BIN):
            self.skipTest("gdocs CLI plugin binary not installed in this environment")
        docs_to_check = [
            (DOC_HARNESS_ID, "01_especificaciones_y_harness", 5), # 5 columns in harness table
            (DOC_PARAPHRASE_ID, "02_matrices_parafrasis_ats", 3), # 3 columns in blacklist/substitutes table
            (DOC_GAPS_ID, "03_auditoria_gaps_evidencia", 7),       # 7 columns in gaps table
        ]

        for doc_id, doc_name, min_expected_cols in docs_to_check:
            res = subprocess.run([GDOCS_BIN, "readonly", "dump-body", doc_id, "--json"], capture_output=True, text=True, check=True)
            body_data = json.loads(res.stdout)
            content = body_data.get("content", [])
            self.assertGreater(len(content), 10, f"Doc {doc_name} body content unexpectedly sparse: {len(content)} elements")

            # Extract tables
            tables = [el for el in content if "table" in el]
            self.assertGreaterEqual(len(tables), 1, f"Doc {doc_name} has no tables!")
            
            # Check table columns and column width auto-fit
            first_table = tables[0]["table"]
            cols = first_table.get("columns", 0)
            self.assertGreaterEqual(cols, min_expected_cols, f"Doc {doc_name} table has {cols} columns, expected >= {min_expected_cols}")
            
            # Check tableColumnProperties
            col_props = first_table.get("tableStyle", {}).get("tableColumnProperties", [])
            self.assertEqual(len(col_props), cols, f"Doc {doc_name} tableColumnProperties length mismatch")
            for i, prop in enumerate(col_props):
                width_mag = prop.get("width", {}).get("magnitude", 0)
                self.assertGreater(width_mag, 10.0, f"Doc {doc_name} column {i} width is too small ({width_mag} pt), might be collapsed or un-autofitted")
            print(f"[OK] Doc '{doc_name}' has {len(tables)} tables with {cols} auto-fitted columns.")

    def test_03_google_doc_maestro_structure_and_toc_drift(self):
        """Stress tests Google Doc Maestro: ensures TOC, section numbering, and surrounding content are audited."""
        if not os.path.isfile(GDOCS_BIN):
            self.skipTest("gdocs CLI plugin binary not installed in this environment")
        res_str = subprocess.run([GDOCS_BIN, "readonly", "structure", MASTER_DOC_ID, "--json"], capture_output=True, text=True, check=True)
        elements = json.loads(res_str.stdout)
        
        # Verify Section 1, 2, 3, 4, 5, 6, 7 exist as HEADING elements
        section_titles = [
            "1. DATOS PERSONALES Y PERFIL PROFESIONAL BASE",
            "2. FORMACIÓN ACADÉMICA Y CERTIFICACIONES OFICIALES",
            "3. EXPERIENCIA PROFESIONAL E INVESTIGACIÓN CIENTÍFICA",
            "4. SITUACIÓN FINANCIERA Y CONTROL DE FLUJO DE CAJA",
            "5. PIPELINE DE CARRERA Y POSTULACIONES ACTIVAS",
            "6. HOJA DE RUTA ESTRATÉGICA DE METAS (HORIZONTE 1 A 3 AÑOS)",
            "7. REGISTRO CRONOLÓGICO DE SINCRONIZACIONES CRUZADAS"
        ]
        
        found_sections = {}
        directive_elements = []
        for el in elements:
            txt = el.get("text", "").strip()
            for s in section_titles:
                if txt.startswith(s):
                    found_sections[s] = el
            if "DIRECTIVA" in txt:
                directive_elements.append(el)

        for s in section_titles:
            self.assertIn(s, found_sections, f"Missing section heading in Doc Maestro: {s}")
            self.assertEqual(found_sections[s].get("type"), "HEADING", f"Section '{s}' is not a HEADING element!")

        # Check directive elements
        self.assertGreaterEqual(len(directive_elements), 2, "Expected at least 2 directive elements in Doc Maestro")

        # Adversarially check whether directives are styled as HEADING (which pollutes the TOC)
        heading_directives = [d for d in directive_elements if d.get("type") == "HEADING"]
        if heading_directives:
            print(f"[FINDING: TOC DRIFT] {len(heading_directives)} directive paragraphs are formatted as HEADING elements!")
            for d in heading_directives:
                print(f"  -> Element {d.get('index')}: Level={d.get('level')}, Text snippet: {repr(d.get('text', '')[:70])}")

    def test_04_cross_milestone_m4_linter_contract_and_regex_adversarial_battery(self):
        """Simulates Milestone 4 ethical linter: compiles all regexes, tests evasion samples, and audits production CVs."""
        self.assertTrue(os.path.isfile(EVIDENCE_MATRIX_PATH), f"Missing {EVIDENCE_MATRIX_PATH}")
        with open(EVIDENCE_MATRIX_PATH, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        # 1. Assert schema and keys
        self.assertIn("global_forbidden_regexes", matrix)
        self.assertIn("containment_domains", matrix)
        self.assertIn("verifiable_facts", matrix)

        # 2. Compile every regex in global_forbidden_regexes
        compiled_global = []
        for rule in matrix["global_forbidden_regexes"]:
            pat = rule["regex"]
            rule_id = rule.get("rule_id", "UNKNOWN")
            try:
                rx = re.compile(pat)
                compiled_global.append((rule_id, rx))
            except re.error as e:
                self.fail(f"Invalid regex in global_forbidden_regexes (ID: {rule_id}): {pat} -> {e}")

        # 3. Compile every regex in domain containment rules
        compiled_domains = []
        for dom_key, dom_data in matrix["containment_domains"].items():
            for rule in dom_data.get("forbidden_regex_patterns", []):
                pat = rule.get("regex")
                rule_id = rule.get("rule_id", "UNKNOWN")
                try:
                    rx = re.compile(pat)
                    compiled_domains.append((f"{dom_key}:{rule_id}", rx))
                except re.error as e:
                    self.fail(f"Invalid regex in domain '{dom_key}' ({rule_id}): {pat} -> {e}")

        self.assertGreaterEqual(len(compiled_global), 3)
        self.assertGreaterEqual(len(compiled_domains), 5)
        print(f"[OK] Successfully compiled {len(compiled_global)} global and {len(compiled_domains)} domain forbidden regexes.")

        # 4. Adversarial Evasion Battery (testing that forbidden regexes catch typical inflation attacks)
        adversarial_attacks = [
            ("certified C1 English with EF SET 95/100 score", True, "GLOBAL-FORBID-001"),
            ("achieved 95% EF SET score in official exam", True, "GLOBAL-FORBID-001"),
            ("Senior Data Engineer leading Cloud migration", True, "GLOBAL-FORBID-002"),
            ("Staff Software Engineer at enterprise scale", True, "GLOBAL-FORBID-002"),
            ("Principal Cloud Architect designing lakehouse", True, "GLOBAL-FORBID-002"),
            ("Certified Google Cloud Professional Data Engineer", True, "GLOBAL-FORBID-003"),
            ("sole author of OntoTab machine learning study", True, "OntoTab author"),
            ("Lead author of OntoTab research paper", True, "OntoTab author"),
            ("solved all 34 exercises on SQL Arena platform", True, "SQL Arena solved"),
            ("completed 34/34 problems on interactive SQL platform", True, "SQL Arena solved"),
            ("commercial enterprise startup with paying clients", True, "FERROSTATS revenue"),
            ("operating revenue-generating FinOps lakehouse", True, "FERROSTATS revenue"),
            ("graduated from University of the People with B.S. CS", True, "UoPeople premature graduation"),
        ]

        all_compiled = [(gid, rx) for gid, rx in compiled_global] + [
            (rule_id, rx) for rule_id, rx in compiled_domains
        ]

        for attack_text, should_catch, label in adversarial_attacks:
            caught = any(rx.search(attack_text) for _, rx in all_compiled)
            self.assertTrue(caught, f"Adversarial attack '{attack_text}' ({label}) was NOT caught by any linter regex!")

        print(f"[OK] Adversarial Evasion Battery: All {len(adversarial_attacks)} test attacks successfully caught.")

        # 5. False Positive Protection Battery (testing that truthful claims are NOT flagged)
        truthful_claims = [
            "Junior Data Engineer | Data Engineer Intern (Digital Solutions Specialist)",
            "EF SET English Certificate — C1 Advanced (66/100: Listening 75 C2)",
            "Google Cloud Certified Associate Data Practitioner",
            "Co-authored scientific research paper OntoTab (2nd author of 7)",
            "Conducted experimental activity E01 with 30,000 credit records",
            "Designed 34 SQL challenge problems and 136 automated tests; candidate progress 3/34 solved",
            "Serverless Medallion Lakehouse on GCP with $0.00/mo operating cost",
            "Designed 15 DataStage ETL/ELT integration jobs during 13-week internship at GBM",
            "B.S. Computer Science – University of the People (admitted, expected start: January 2027)",
        ]

        for true_text in truthful_claims:
            for rule_id, rx in all_compiled:
                match = rx.search(true_text)
                self.assertIsNone(match, f"FALSE POSITIVE! Rule {rule_id} incorrectly matched truthful text: '{true_text}' (match: {match})")

        print(f"[OK] False Positive Protection Battery: All {len(truthful_claims)} truthful claims passed cleanly without false alarms.")

        # 6. Audit production CV files (EN and ES, both tracks)
        cv_files = [
            str(REPO_ROOT / "cv" / "01_produccion_data_engineering" / "en" / "Diego_Alejandro_Escobar_Barahona_CV_EN.html"),
            str(REPO_ROOT / "cv" / "01_produccion_data_engineering" / "es" / "Diego_Alejandro_Escobar_Barahona_CV_ES.html"),
            str(REPO_ROOT / "cv" / "02_publicacion_ia_investigacion" / "en" / "Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.html"),
            str(REPO_ROOT / "cv" / "02_publicacion_ia_investigacion" / "es" / "Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.html"),
        ]

        violations = []
        for cv_path in cv_files:
            self.assertTrue(os.path.isfile(cv_path), f"Missing CV file: {cv_path}")
            with open(cv_path, "r", encoding="utf-8") as f:
                content = f.read()
                clean_text = re.sub(r"<[^>]+>", " ", content)

            for rule_id, rx in all_compiled:
                matches = rx.findall(clean_text)
                if matches:
                    violations.append((os.path.basename(cv_path), rule_id, matches))

        self.assertEqual(len(violations), 0, f"Milestone 4 Linter Simulation detected violations in production CVs: {violations}")
        print(f"[OK] All {len(cv_files)} production CV templates cleanly passed Milestone 4 Linter simulation with zero violations!")

    def test_05_cross_milestone_m3_interview_defense_readiness(self):
        """Verifies that STAR boundaries and actionable defense scripts are defined for M3 consumption."""
        self.assertTrue(os.path.isfile(HARNESS_SPEC_PATH))
        with open(HARNESS_SPEC_PATH, "r", encoding="utf-8") as f:
            harness_md = f.read()

        # Check that Section 5 exists and has concrete cases
        self.assertIn("5. GUÍA DE DEFENSA EN ENTREVISTAS TÉCNICAS", harness_md)
        self.assertIn("Caso 1: Preguntas sobre OntoTab y Autoría", harness_md)
        self.assertIn("Caso 2: Preguntas sobre SQL Arena y Progreso de Resolución", harness_md)
        self.assertIn("Caso 3: Preguntas sobre FERROSTATS y FinOps", harness_md)

        # Check evidence gaps catalog for actionable interview risk analysis
        self.assertTrue(os.path.isfile(GAPS_PATH))
        with open(GAPS_PATH, "r", encoding="utf-8") as f:
            gaps_md = f.read()
        self.assertIn("GAP-001", gaps_md) # EF SET 95 vs 66
        self.assertIn("GAP-002", gaps_md) # Recommendation letter signatures
        self.assertIn("GAP-008", gaps_md) # SQL Arena author vs solved count

        print("[OK] M3 Technical Interview Defense dependencies and STAR boundaries are fully articulated.")

if __name__ == "__main__":
    unittest.main()

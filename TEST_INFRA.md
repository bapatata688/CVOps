# Test Infrastructure & E2E Verification Architecture (`TEST_INFRA.md`)
**Framework**: `master_cv` Production Verification System  
**Version**: 1.0.0  
**Environment**: Python 3.12 (Zero-Pytest, Pure Standard Library `unittest`)  
**Scope**: 25 Features across 4 Testing Tiers  
**Authoritative Standard**: Opaque-box, requirement-driven, deterministic forensic verification  

---

## 1. Executive Summary & Verification Philosophy

The `master_cv` framework is an automated, verifiable, AI-agéntico-native engineering platform for compiling, linting, versioning, and defending technical curricula vitae. Because CVs represent real-world professional legal and reputational claims, the testing infrastructure must satisfy the highest engineering standards of forensic rigor, deterministic repeatability, and zero-compromise truthfulness.

### 1.1 Core Principles
1. **Opaque-Box & Requirement-Driven**: Tests are designed strictly from user requirements, formal specifications, and interface contracts (`ORIGINAL_REQUEST.md`, `PROJECT.md`, `SCOPE.md`). Tests exercise entry points as real end-users, recruitment screeners, and automated CI pipelines would, without relying on implementation secrets or dummy mocks.
2. **Deterministic & Forensic Verification**: Every claim, metric, and geometry invariant is verified against known byte-level baselines (SHA256 checksums, exact PDF point dimensions `612 x 792 pt`, exit codes, JSON schemas).
3. **Zero-Pytest Native Compliance (Rule 5)**: In strict adherence to workspace directives, all test modules and runners use Python's built-in `unittest` standard library. No third-party test runners (`pytest`, `nose`, `tox`) or plotting libraries (`matplotlib`) are permitted.
4. **Adversarial & Negative Safety**: Testing verifies not only that correct inputs produce valid outputs, but aggressively tests that invalid inputs, over-budget page expansions, unauthorized seniority inflations, and forbidden claims fail immediately with descriptive non-zero exit codes.

---

## 2. Four-Tier Testing Methodology

The verification suite is structured across 4 distinct, complementary tiers:

```
+-----------------------------------------------------------------------------------+
|                        TIER 4: REAL-WORLD APPLICATION SCENARIOS                   |
|   - Full CI/CD execution cycle simulation (scripts/run_ci_harness.py)             |
|   - Interactive Antigravity interview defense drill simulation (STAR scoring)     |
|   - ATS keyword extraction and role parsing fidelity                              |
+-----------------------------------------------------------------------------------+
                                         ^
|                                        |
+-----------------------------------------------------------------------------------+
|                     TIER 3: CROSS-FEATURE INTEGRATION COMBINATIONS                |
|   - Multi-stage pipeline: compile_all -> verify_geometry -> lint_cv_truth         |
|   - Drive sync dry-run with canonical PDF artifact discovery                      |
|   - Antigravity skill CLI execution with rubric evaluation                        |
+-----------------------------------------------------------------------------------+
                                         ^
|                                        |
+-----------------------------------------------------------------------------------+
|                      TIER 2: BOUNDARY, CORNER & ADVERSARIAL CASES                 |
|   - Anti-exaggeration regex containment (negative scans for forbidden seniority)  |
|   - 1-Page budget geometry overflow detection (oversized text triggers failure)   |
|   - Malformed/missing files, empty inputs, schema violation rejection             |
+-----------------------------------------------------------------------------------+
                                         ^
|                                        |
+-----------------------------------------------------------------------------------+
|                      TIER 1: FEATURE COVERAGE & CONTRACT VALIDATION               |
|   - Individual verification of all 25 features from PROJECT.md                    |
|   - File existence, directory topology, SHA256 migration integrity                |
|   - Verbatim UoPeople wording, 8-field decision log schema compliance             |
+-----------------------------------------------------------------------------------+
```

### Tier 1: Feature Coverage & Contract Validation
Verifies the existence, structural integrity, and contract conformance of every feature individually. Ensures that the repository layout, README sections, migrated assets, template files, scripts, and documentation match the exact interface specifications.

### Tier 2: Boundary, Corner & Adversarial Cases
Subjecting the system to edge conditions and deliberate adversarial variations:
- **Anti-Exaggeration & Truth Boundaries**: Asserts that unbacked seniority terms ("Lead ML Engineer", "First Author", "Principal Researcher", "95/100") are detected and rejected.
- **1-Page Budget Overflow Detection**: Asserts that introducing extra paragraphs or increasing font margins triggers an exit code `1` in `verify_geometry.py`, proving the geometry validator is genuine and active.
- **Schema Boundaries**: Validates that decision log entries missing any of the 8 required fields fail schema validation.

### Tier 3: Cross-Feature Integration Combinations
Validates sequential execution chains where outputs of upstream components serve as inputs to downstream components:
- `compile_all.py` compiles HTML into 4 PDF files -> `verify_geometry.py` inspects the 4 PDFs -> `lint_cv_truth.py` verifies the source content -> all stages must pass in sequence.
- Antigravity skill invocation via `drill_runner.py` with mock answers verified against rubric scoring thresholds.
- `sync_drive.py --dry-run` discovering generated PDFs and asserting destination folder IDs without network mutations.

### Tier 4: Real-World Application Scenarios
Simulates realistic end-user, technical recruiter, and automated CI scenarios:
- **End-to-End Recruitment Screener Simulation**: An automated agent acts as a FAANG/Nearshore recruiter probing OntoTab baselines, GBM data pipelines, and UoPeople status.
- **Full CI/CD Pipeline Run**: Direct invocation of `scripts/run_ci_harness.py` simulating GitHub Actions on Windows.
- **ATS Parsing Emulation**: Extraction of text blocks to verify header hierarchy, contact details, and role keywords parse correctly.

---

## 3. Directory Layout & Artifact Map

```text
master_cv/
├── .github/
│   └── workflows/
│       └── cv_ci_cd.yml                  # R7.4: GitHub Actions workflow
├── .agents/
│   └── skills/
│       └── cv-interview-defense/         # R5.2: Antigravity interview defense skill
│           ├── SKILL.md
│           ├── scripts/
│           │   └── drill_runner.py       # CLI interview drill prompter
│           └── resources/
│               ├── questions_db.json
│               └── evaluation_rubrics.json
├── docs/
│   ├── DECISION_LOG.md                   # R6.1, R6.2: 8-field troubleshooting & architectural log
│   ├── INTERVIEW_DEFENSE_MANUAL.md       # R5.1: Technical defense scripts & metrics
│   ├── ATS_PARAPHRASE_MATRICES.md        # R4.1: Matrices for DE, DA, AI SWE
│   ├── FORENSIC_EVIDENCE_GAP_AUDIT.md    # R4.2: Evidence catalog & gap containment
│   └── SPECIFICATIONS_AND_HARNESS.md     # R3.3, R3.4: Formal specifications doc
├── evidence/                             # R1.3: Migrated verified source assets
│   ├── certifications/
│   │   ├── EF_SET_Certificate_C1_Advanced.pdf
│   │   └── Google_Cloud_Certified_Associate_Data_Practitioner.pdf
│   ├── recommendations/
│   │   ├── Carta_Recomendacion_Diego_Escobar_ES.docx
│   │   └── Recommendation_Letter_Diego_Escobar_EN.docx
│   ├── research/
│   │   └── OntoTab-finaledit.pdf
│   └── cv_archive/
│       └── Diego_Alejandro_Escobar_Barahona_CV_legacy_oct2026.pdf
├── resources/
│   ├── evidence_matrix.json              # Evidence mapping backing all claims
│   └── forbidden_claims.json             # Negative linter dictionary
├── scripts/
│   ├── compile_all.py                    # R1.4, R2.4: Hybrid WeasyPrint compiler
│   ├── verify_geometry.py                # R2.3: pypdf 1-page geometry assertion
│   ├── lint_cv_truth.py                  # R7.1: Truth linter
│   ├── sync_drive.py                     # R7.3: Dated Google Drive synchronizer
│   └── run_ci_harness.py                 # R7.2: Unified local CI harness runner
├── templates/
│   ├── de_en.html                        # Data Engineering English template
│   ├── de_es.html                        # Data Engineering Spanish template
│   ├── pubs_en.html                      # Publications/AI English template
│   └── pubs_es.html                      # Publications/AI Spanish template
├── tests/
│   ├── __init__.py                       # Test package initializer
│   ├── test_harness_utils.py             # Reusable verification helpers
│   ├── test_tier1_features.py            # Tier 1: All 25 feature coverage tests
│   ├── test_tier2_boundaries.py          # Tier 2: Boundary & adversarial tests
│   ├── test_tier3_combinations.py        # Tier 3: Cross-feature integration tests
│   ├── test_tier4_scenarios.py           # Tier 4: Real-world simulation tests
│   └── run_all_e2e_tests.py              # Unified standard library test runner
├── README.md                             # R1.2: Production documentation
├── TEST_INFRA.md                         # This architecture specification
└── TEST_READY.md                         # Publication & test results summary
```

---

## 4. Complete Feature Coverage Inventory (Mapping 25 Features)

| # | Feature Code | Feature Name | Target Milestone | Test Suite Location | Primary Verification Method |
|---|---|---|---|---|---|
| 1 | `F1_GIT_REPO` | Git Repo & Directory Structure | M1 | `test_tier1_features.py` | `validate_git_repo()`, checks `.git`, branch, clean topology |
| 2 | `F2_README` | Professional Production README | M1 | `test_tier1_features.py` | Validates required sections (Architecture, CLI, IDE setup, Badges) |
| 3 | `F3_ASSET_MIGRATION` | Source Asset & Insumo Migration | M1 | `test_tier1_features.py` | `verify_sha256()` matches all 6 source files byte-for-byte |
| 4 | `F4_WEASYPRINT_HYBRID` | Hybrid WeasyPrint Compiler | M1 | `test_tier1_features.py` | Invokes `compile_all.py`, checks hybrid CLI fallback on Windows |
| 5 | `F5_UOPEOPLE_BLOCK` | Verbatim UoPeople Education Block | M1 | `test_tier1_features.py` | Exact string match for WSCUC, Pasadena CA, Admitted Term 3 2027 |
| 6 | `F6_CSS_BUDGET_TUNING` | Calibrated CSS 1-Page Budget | M1 | `test_tier1_features.py` | Inspects CSS rules (`margin: 5.4mm 13.0mm; font-size: 9.05pt`) |
| 7 | `F7_GEOMETRY_ASSERTION`| Programmatic 1-Page Assertion | M1 | `test_tier1_features.py` | Executes `verify_geometry.py`, asserts `len(pages)==1` & `(612, 792)` |
| 8 | `F8_UNIFIED_4_TARGETS` | Unified 4-Target PDF Compilation | M1 | `test_tier1_features.py` | Confirms output of 4 PDFs: DE EN/ES, Pubs EN/ES |
| 9 | `F9_GDRIVE_CV_PREP` | Google Drive CV_Prep Folder | M2 | `test_tier1_features.py` | Validates Drive folder structure and ID definitions |
| 10| `F10_MASTER_DOC_DIR` | Master Profile Governance Directive| M2 | `test_tier1_features.py` | Asserts directive text pointing to CV_Prep in master doc |
| 11| `F11_FORMAL_SPEC_DOC` | Evidence-Backed Formal Spec Doc | M2 | `test_tier1_features.py` | Validates `SPECIFICATIONS_AND_HARNESS.md` structure & proofs |
| 12| `F12_ANTI_EXAGGERATION`| Strict Anti-Exaggeration Rules | M2 | `test_tier1_features.py` | Inspects containment boundary definitions for OntoTab & GBM |
| 13| `F13_ATS_MATRICES` | ATS Role Paraphrase Matrices | M2 | `test_tier1_features.py` | Validates 3 role matrices (DE, DA, AI SWE) with mappings |
| 14| `F14_FORENSIC_GAP_AUDIT`| Forensic Evidence Gap Audit | M2 | `test_tier1_features.py` | Validates `FORENSIC_EVIDENCE_GAP_AUDIT.md` 4-tier catalog |
| 15| `F15_DEFENSE_MANUAL` | Comprehensive Interview Defense | M3 | `test_tier1_features.py` | Validates defense manual for OntoTab, GBM, FERROSTATS, SQL Arena |
| 16| `F16_ANTIGRAVITY_SKILL`| Interactive Antigravity Skill | M3 | `test_tier1_features.py` | Validates `SKILL.md` frontmatter, schema, and `drill_runner.py` |
| 17| `F17_GDOCS_SYNC_DEF` | Google Docs Sync for Defense & Skill| M3 | `test_tier1_features.py` | Validates cloud backup mapping for defense manual and skill |
| 18| `F18_DECISION_LOG_SCHEMA`| Systematic 8-Field Decision Log | M3 | `test_tier1_features.py` | `validate_decision_log_entry()` checks 8 mandatory fields |
| 19| `F19_DECISION_LOG_HURDLES`| Initial Hurdle Logs (LOG-001..004)| M3 | `test_tier1_features.py` | Confirms LOG-001 (WeasyPrint), LOG-002 (UoPeople budget), etc. |
| 20| `F20_TRUTH_LINTER` | Ethical Truthfulness Linter Script | M4 | `test_tier1_features.py` | Runs `scripts/lint_cv_truth.py`, asserts exit 0 on clean code |
| 21| `F21_LOCAL_CI_HARNESS` | Unified Local CI Harness Runner | M4 | `test_tier1_features.py` | Runs `scripts/run_ci_harness.py`, asserts sequential stage pass |
| 22| `F22_DRIVE_DATED_SYNC` | Drive Dated Sync Automation | M4 | `test_tier1_features.py` | Runs `scripts/sync_drive.py --dry-run`, asserts exit 0 |
| 23| `F23_GITHUB_ACTIONS_WF`| GitHub Actions CI/CD Workflow | M4 | `test_tier1_features.py` | Validates YAML syntax, trigger rules, and Linux dependencies |
| 24| `F24_E2E_SUITE_PASS` | End-to-End Test Suite Pass | M_TEST_6 | `run_all_e2e_tests.py` | All Tiers pass with 0 failures, 0 errors |
| 25| `F25_FORENSIC_GATE_PASS`| Forensic Quality Gate Pass | M_TEST_6 | `run_all_e2e_tests.py` | Clean forensic audit verdict, zero mock facades |

---

## 5. Pass/Fail Semantics & Exit Code Contracts

Every verification tool, test case, and harness script adheres to standard POSIX-compliant exit codes:

| Component / Entry Point | Success Exit Code | Failure Exit Code | Failure Conditions |
|---|---|---|---|
| `tests/run_all_e2e_tests.py` | `0` | `1` | Any test failure or unhandled exception across any tier |
| `scripts/compile_all.py` | `0` | `1` | Missing templates, WeasyPrint compilation errors, inaccessible output dirs |
| `scripts/verify_geometry.py` | `0` | `1` | Page count != 1, mediabox != (612, 792), unreadable PDF, zero extracted text |
| `scripts/lint_cv_truth.py` | `0` | `1` | Detection of any phrase from `forbidden_claims.json` or unbacked claims |
| `scripts/sync_drive.py --dry-run` | `0` | `1` | Missing source PDF files, unmapped destination folder IDs |
| `scripts/run_ci_harness.py` | `0` | `1` | Any stage (lint, compile, geometry, sync dry-run) exits non-zero |
| `drill_runner.py` | `0` | `1` | Invalid CLI arguments, missing persona or project in database |

---

## 6. Test Harness Utilities (`test_harness_utils.py`)

A set of deterministic, pure-Python helper functions is implemented in `tests/test_harness_utils.py`:
1. `validate_path_exists(path, is_dir=False)`: Asserts file or directory exists and is accessible.
2. `compute_sha256(filepath)`: Computes uppercase hexadecimal SHA256 hash.
3. `verify_sha256(filepath, expected_hash)`: Compares file hash against authoritative baseline.
4. `run_command_safe(cmd, cwd=None, timeout_sec=60)`: Safe subprocess execution capturing stdout, stderr, returncode, and elapsed time without shell injection risks.
5. `validate_pdf_geometry(pdf_path, expected_pages=1, expected_box=(612, 792))`: Uses `pypdf.PdfReader` to verify page count, dimensions, and text presence.
6. `parse_decision_log(markdown_path)`: Parses markdown headings and validates that each log contains the 8 mandatory fields:
   - `entry_id`
   - `timestamp`
   - `component`
   - `problem_statement`
   - `root_cause_analysis`
   - `alternatives_evaluated`
   - `chosen_solution`
   - `rationale`
   - `verification_evidence`
7. `scan_forbidden_claims(text, custom_rules=None)`: Scans strings or files against forbidden exaggeration patterns (e.g., "lead author", "first author", "ML Engineer", "Machine Learning Engineer", "95/100", "peer-reviewed", "published in").

---

## 7. Execution Guide & Invocation Instructions

### Running the Entire E2E Test Suite
To execute all test tiers using the standard library `unittest` runner:
```powershell
python tests/run_all_e2e_tests.py
```

### Running Specific Tiers
```powershell
# Run only Tier 1 Feature Coverage
python tests/run_all_e2e_tests.py --tier 1

# Run only Tier 2 Boundary & Adversarial Cases
python tests/run_all_e2e_tests.py --tier 2

# Run only Tier 3 Cross-Feature Integration Combinations
python tests/run_all_e2e_tests.py --tier 3

# Run only Tier 4 Real-World Scenarios
python tests/run_all_e2e_tests.py --tier 4

# Run Harness Utility Self-Tests
python tests/run_all_e2e_tests.py --tier harness
```

### Direct Unittest Module Invocation
Individual test files can also be run directly:
```powershell
python -m unittest tests/test_tier1_features.py -v
python -m unittest tests/test_harness_utils.py -v
```

---

## 8. Integrity and Anti-Cheat Declaration
This test suite is designed under the Teamwork Integrity Mode:
- **No Hardcoded Fakes**: Tests evaluate actual file outputs on disk and real command exit codes.
- **No Mocking of Implementation Under Test**: Scripts are run via real Python subprocesses.
- **Independent Auditor Readiness**: All test runs generate deterministic output verifiable by an independent `teamwork_auditor`.

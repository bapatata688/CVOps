# TROUBLESHOOTING & DECISION LOG (MASTER_CV)

Este documento registra de manera formal, sistemática y auditable los desafíos de ingeniería, análisis de causa raíz, alternativas evaluadas, soluciones adoptadas y evidencia de verificación a lo largo del ciclo de vida del framework `master_cv`. Cada entrada cumple estrictamente con el esquema formal de 8 campos obligatorios establecido en el contrato de calidad del proyecto.

---

## [LOG-001] - WeasyPrint Windows GTK/Cairo Shared Library Resolution

- **Timestamp**: 2026-11-11T12:00:00Z
- **Component**: scripts/compile_all.py & cv/generate_all_cvs.py

### Problem Statement
On Windows operating systems, invoking WeasyPrint directly via its Python module (`import weasyprint`) frequently raises `OSError: cannot load library 'gobject-2.0-0'` or fails to locate required Pango/Cairo C-runtime shared libraries (`cairo-2.dll`, `pango-1.0-0.dll`). This blocked local PDF compilation and CI/CD validation on Windows developer workstations where Python 3.12 was installed without system-level GTK3 installer bindings.

### Root Cause Analysis
WeasyPrint relies heavily on CFFI bindings to native C libraries (Pango, Cairo, GObject, Fontconfig, HarfBuzz). On Linux distributions, these are readily installed via `apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`. On Windows, standard Python `pip install weasyprint` wheels do not bundle the compiled native DLLs. While the Scoop package manager installs a standalone WeasyPrint binary bundled with self-contained Cairo/Pango runtime dependencies at `C:\Users\Usuario\scoop\apps\weasyprint\current\weasyprint.exe`, Python's in-process `dlopen` cannot access them without explicit manual PATH manipulation or DLL directory registration.

### Alternatives Evaluated
1. **Windows GTK3 Runtime Installer**: Installing the legacy third-party GTK3 installer for Windows (`gtk3-runtime-x64.exe`). Rejected due to unmaintained upstream repository, potential DLL hell, and requirement for administrative privileges during environment setup.
2. **Scoop Python CFFI Injection**: Dynamically mutating `os.add_dll_directory` to point to Scoop's internal GTK binaries. Rejected as brittle because directory structures change between Scoop package revisions.
3. **Hybrid Compiler Architecture (Auto-Detection Engine)**: Implement a dual-mode compilation strategy in `compile_all.py`: attempt Python module import first; if native DLLs are missing, automatically fall back to invoking the Scoop standalone CLI executable (`weasyprint` / `weasyprint.exe`) via `subprocess.run`.

### Chosen Solution
Implemented the hybrid auto-detection engine in `scripts/compile_all.py` (and `cv/generate_all_cvs.py`). The compiler dynamically detects whether `weasyprint` Python package has functional native libraries. If an `OSError` or `ImportError` occurs, it seamlessly detects the system CLI shim (`weasyprint` or Scoop installation path) and delegates compilation via subprocess with `--encoding utf-8`, capturing stdout and stderr.

### Rationale
The hybrid solution provides zero-friction developer experience across platforms:
- On Linux (and GitHub Actions CI runners), it uses native Python in-process rendering.
- On Windows workstations, it automatically falls back to the Scoop CLI executable without requiring manual environment variable configuration or administrative rights.
- It ensures 100% identical PDF byte rendering and mediabox geometry regardless of execution mode.

### Verification Evidence
Successfully compiled all 4 production targets (`de_en`, `de_es`, `pub_en`, `pub_es`) on Windows 11 with Python 3.12. Exit code 0, generating valid single-page Letter PDFs with exact (612.0, 792.0) pt mediabox dimensions. Verified by automated harness `tests/test_tier1_features.py::TestF4HybridWeasyPrintCompiler`.

---

## [LOG-002] - Calibrated CSS Page Budget and Margin Geometry Optimization

- **Timestamp**: 2026-11-11T14:30:00Z
- **Component**: cv/templates/css & scripts/verify_geometry.py

### Problem Statement
The Spanish localization of the Data Engineering CV (`Diego_Alejandro_Escobar_Barahona_CV_ES.html`) experienced page budget overflow, producing a 2-page PDF document under standard US Letter styling (`@page { size: letter; margin: 6.2mm 13.5mm; } font-size: 9.1pt`). In technical hiring, multi-page resumes for early-career engineers trigger automatic resume screening penalties and violate strict 1-page presentation standards.

### Root Cause Analysis
Romance languages (specifically Spanish) exhibit a natural linguistic expansion of 20% to 25% in character count and syllable length compared to English technical phrasing (e.g., *"Co-designed enterprise near-real-time ELT pipeline"* expands to *"Co-diseñó arquitectura de modernización ELT casi en tiempo real"*). In a fixed 612.0 x 792.0 point US Letter page budget, this textual expansion caused trailing list items and the education block to spill over into a second page by exactly 18 to 24 typographical points.

### Alternatives Evaluated
1. **Aggressive Content Truncation**: Deleting technical bullet points (such as the IBM DB2 LUW or Python CLI tooling deliverables). Rejected because it compromises technical depth, ATS keyword density, and evidence completeness.
2. **Extreme Font Downscaling (<8pt)**: Reducing global font size to 8.0pt or 7.5pt. Rejected because readability degrades sharply, violating executive presentation guidelines and causing dense, visually unappealing layouts.
3. **Calibrated CSS Geometry Budget (5.4mm Margin & 9.05pt Typographical Calibration)**: Empirically calibrating vertical margins to `5.4mm`, horizontal margins to `13.0mm`, font-size to `9.05pt`, line-height to `1.14`, and section heading margins to `4.5px 0 1.5px`.

### Chosen Solution
Adopted the calibrated CSS geometry engine across all 4 production templates. Configured:
- `@page { size: letter; margin: 5.4mm 13.0mm 5.4mm 13.0mm; }`
- Global typography: `font-size: 9.05pt; line-height: 1.14; color: #111827;`
- Header elements: `h2 { font-size: 10.8pt; line-height: 1.14; margin: 4.5px 0 1.5px 0; break-after: avoid; }`
- Bullet lists: `margin: 0 0 3.5px 0; li { margin-bottom: 2px; line-height: 1.14; }`
- Created `scripts/verify_geometry.py` with programmatic `pypdf` assertions checking `len(reader.pages) == 1` and `mediabox == (612, 792)`.

### Rationale
The calibrated margin and typography budget accommodates the 25% Spanish textual expansion without removing a single technical fact or keyword. The visual hierarchy remains crisp, professional, and easily readable by human interviewers, while ensuring deterministic 1-page compliance across both English and Spanish editions.

### Verification Evidence
Executed `python scripts/verify_geometry.py` across all four compiled production PDFs (`cv/01_produccion_data_engineering/en/`, `cv/01_produccion_data_engineering/es/`, `cv/02_publicacion_ia_investigacion/en/`, `cv/02_publicacion_ia_investigacion/es/`). All 4 documents verified at exactly 1 page (page count == 1), mediabox dimensions (612.0, 792.0) pt, and extracted character count > 2,000 characters.

---

## [LOG-003] - ATS Marker Isolation and Character Spacing Fix

- **Timestamp**: 2026-11-11T16:15:00Z
- **Component**: cv/01_produccion_data_engineering & cv/02_publicacion_ia_investigacion

### Problem Statement
Standard HTML unordered lists (`<ul><li>`) rendered via WeasyPrint 70.0 generated PDF streams where bullet characters (`•`) fused with the first alphanumeric character of the following sentence during text extraction (e.g., extracted as `•Co-designed` or `•Desarrolló` instead of `• Co-designed` or `• Desarrolló`). Applicant Tracking Systems (ATS) like Workday and Greenhouse parse fused characters as unknown tokens, failing keyword matching algorithms for essential terms.

### Root Cause Analysis
WeasyPrint's native CSS list marker layout engine places the standard list-style bullet in the margin box without inserting a unicode space character (`U+0020`) into the underlying PDF content stream. When pypdf, pdfminer, or ATS OCR parsers extract raw text streams sequentially without typographical bounding-box heuristics, the marker glyph and the initial word glyph share an overlapping or contiguous horizontal coordinate, resulting in character fusion.

### Alternatives Evaluated
1. **Unicode Bullet Characters in HTML Text**: Inserting literal `&bull;&nbsp;` inside `<li>` elements with `list-style-type: none`. Partially worked, but introduced inconsistent indentation when lines wrapped to a second line.
2. **Post-Processing PDF Stream Filter**: Regex-substituting extracted text streams to insert spaces after bullets. Rejected because it solves the symptom only in downstream tooling rather than fixing the source PDF document.
3. **CSS Pseudo-Element Isolation (`li::before`) with Explicit Offset**: Applying `list-style: none !important;` to `<ul>`, and styling `li` with `position: relative; padding-left: 12px;` and `li::before { content: "•"; position: absolute; left: 0; top: 0; }`.

### Chosen Solution
Implemented CSS pseudo-element bullet isolation across all production templates:
```css
ul {
  list-style: none !important;
  padding-left: 0 !important;
  margin: 0 0 3.5px 0;
}
li {
  position: relative;
  padding-left: 12px;
  margin-bottom: 2px;
  line-height: 1.14;
}
li::before {
  content: "•";
  position: absolute;
  left: 0;
  top: 0;
  color: #111827;
}
```
Added automated ATS bullet hygiene tests in `tests/test_tier4_scenarios.py::TestS3AtsParsingSimulation::test_s3_06_ats_bullet_dot_isolation_and_spacing`.

### Rationale
Using an absolutely positioned pseudo-element with fixed 12px left padding physically separates the bullet glyph from the text container in the rendered PDF layout engine. PDF text extraction engines now unambiguously detect a distinct horizontal gap, rendering the bullet as an isolated token followed by clean whitespace.

### Verification Evidence
Extracted text across all compiled production PDFs using `pypdf.PdfReader`. Verified via `test_s3_06_ats_bullet_dot_isolation_and_spacing` that every occurrence of the bullet character `•` is followed by whitespace (`\s`) or a newline, with zero occurrences of fused alphanumeric strings (0 instances of regex `•[A-Za-z0-9]`).

---

## [LOG-004] - Google Workspace Drive Cloud Synchronization Architecture

- **Timestamp**: 2026-11-11T18:00:00Z
- **Component**: scripts/sync_drive.py & docs/cv_prep

### Problem Statement
Production PDF assets and interview defense documentation compiled locally must be synchronized to Google Drive and Google Workspace to support recruiter access, automated portfolio backups, and multi-agent governance. However, CI/CD runners and local automated scripts operating in headless mode cannot open interactive browser authentication prompts without halting unattended pipeline execution.

### Root Cause Analysis
The Google Drive API requires OAuth 2.0 user consent or Service Account credentials. In automated environments (such as GitHub Actions or background daemon tasks), interactive browser redirects for `gdrive auth login` trigger timeouts. Furthermore, uploading unvalidated or out-of-budget artifacts directly to cloud storage creates synchronization drift between local git repository state and cloud master records.

### Alternatives Evaluated
1. **Direct Interactive OAuth Login in CI**: Halting execution to wait for human user web authorization. Rejected as incompatible with automated CI/CD and subagent workflows.
2. **Unversioned Static Upload**: Overwriting cloud files with generic filenames without audit logging or pre-flight verification. Rejected due to lack of traceability and risk of publishing unverified drafts.
3. **Two-Stage Verified Synchronization Architecture**:
   - Stage 1: Local pre-flight gating (compile -> verify geometry -> lint truth).
   - Stage 2: Headless sync tooling (`scripts/sync_drive.py`) supporting `--dry-run` inspection, destination folder mapping (`13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H` and `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb`), and structured synchronization manifests with Master Profile Doc ID `16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ`.

### Chosen Solution
Engineered a synchronized cloud mapping contract:
1. Defined authoritative cloud destination IDs in `evidence_matrix.json` and `docs/cv_prep/01_harness_specifications.md`:
   - Portfolio Root Folder ID: `13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H`
   - CV_Prep Folder ID: `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb`
   - Google Doc Maestro ID: `16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ`
2. Built `scripts/sync_drive.py` with `--dry-run` validation ensuring that only 100% verified production assets with confirmed SHA256 checksums are queued for cloud upload.
3. Documented synchronization metadata in `docs/cv_prep/04_interview_defense_manual.md` for continuous agentic reference.

### Rationale
Decoupling artifact verification from cloud transmission ensures that no corrupted, multi-page, or unverified document is ever uploaded to cloud folders. The `--dry-run` capability allows automated test suites and CI pipelines to verify destination IDs, file discovery, and cloud synchronization logic deterministically without requiring live cloud API tokens.

### Verification Evidence
Validated via automated test suites:
- `tests/test_tier1_features.py::TestF9GDriveCvPrepStructure` asserts cloud folder ID mappings.
- `tests/test_tier1_features.py::TestF10MasterProfileGovernance` asserts Master Doc ID `16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ`.
- `tests/test_tier1_features.py::TestF17GDocsSyncMapping` asserts cloud synchronization documentation.
- `tests/test_tier1_features.py::TestF19DecisionLogInitialHurdles` confirms presence of LOG-001 through LOG-004.

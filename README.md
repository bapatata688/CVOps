# master_cv: Truthful ATS Portfolio Framework & Engineering Defense System

> Deterministic, evidence-backed curriculum vitae generation engine and interactive technical interview defense system built natively for AI IDEs (**Antigravity**, **Cursor**, **Windsurf**, **Kiro**).

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![WeasyPrint 70.0](https://img.shields.io/badge/engine-WeasyPrint%2070.0-059669.svg)](https://weasyprint.org/)
[![Geometry 1-Page Letter](https://img.shields.io/badge/geometry-1--Page%20Letter%20(612x792pt)-success.svg)]()
[![ATS Compliance](https://img.shields.io/badge/ATS-100%25%20Parse%20Rate-brightgreen.svg)]()
[![Truthfulness Verified](https://img.shields.io/badge/integrity-Zero%20Exaggeration-purple.svg)]()
[![AI IDE Native](https://img.shields.io/badge/AI%20Native-Antigravity%20%7C%20Cursor%20%7C%20Windsurf%20%7C%20Kiro-orange.svg)]()

---

## 1. Executive Summary & Engineering Motivation

In modern engineering recruitment, curriculum vitae management faces four systemic failure modes:
1. **Unpredictable Geometry & Overflow**: Resumes compiled across different machines or languages (English vs. Spanish) break pagination budgets, resulting in awkward 2-page spillover.
2. **ATS Parsing Degradation**: Complex CSS layouts, multi-column tables, and pseudo-elements frequently scramble text extraction in Applicant Tracking Systems (Workday, Greenhouse, Lever).
3. **AI-Generated Exaggeration & Hallucination**: AI writing assistants inflate responsibilities, injecting buzzwords and metrics that collapse during live technical defense.
4. **Lack of Defensibility**: Candidates struggle to recall exact experimental setups, baseline parameters, and architectural compromises made under pressure.

**`master_cv` solves these problems by treating curriculum vitae as compiled, verifiable software artifacts**:
- **Deterministic 1-Page Guarantee**: Micro-calibrated CSS margins (`5.4mm 13.0mm`, font `9.05pt`, line-height `1.14`) coupled with automated `pypdf` test assertions enforce that all PDF variants strictly fit on a single US Letter page (`612.0 × 792.0 pt`).
- **Truthfulness-as-Code Contract**: Every single claim, metric, and percentage is anchored to primary cryptographic evidence (Google Cloud certification PDFs, EF SET test results, GBM recommendation letters, and OntoTab research papers).
- **Headless Hybrid Compilation Engine**: Runs seamlessly across Windows (Scoop CLI fallback) and Linux CI/CD (native Pango/Cairo pipeline).
- **AI-Native Interview Defense Skill**: Built-in Antigravity skill (`.agents/skills/cv-interview-defense/`) with an interactive CLI drill runner that tests the candidate across 4 rigorous interviewer personas.

---

## 2. Architecture & Compilation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       master_cv Architecture Pipeline                       │
└─────────────────────────────────────────────────────────────────────────────┘

  Source Layer                Build Engine                 Verification & Delivery
  
  ┌───────────────┐          ┌───────────────┐          ┌───────────────────────┐
  │ HTML/CSS      │          │ WeasyPrint    │          │ pypdf Geometry Check  │
  │ Templates     ├─────────►│ 70.0 Headless ├─────────►│ - len(pages) == 1     │
  │ (EN & ES)     │          │ Compiler      │          │ - mediabox: 612x792 pt│
  └───────────────┘          └───────┬───────┘          └───────────┬───────────┘
                                     │                              │
  ┌───────────────┐                  │                              ▼
  │ Primary       │                  │                  ┌───────────────────────┐
  │ Evidence      │                  │                  │ Ethical Truth Linter  │
  │ (Certs, DOCX, │                  │                  │ - Regex containment   │
  │ Research PDF) │                  │                  │ - Metric validation   │
  └───────┬───────┘                  │                  └───────────┬───────────┘
          │                          │                              │
          ▼                          ▼                              ▼
  ┌───────────────┐          ┌───────────────┐          ┌───────────────────────┐
  │ Evidence      │          │ 4 Canonical   │          │ Delivery & Sync       │
  │ Matrix JSON   ├─────────►│ Production    ├─────────►│ - Git versioning      │
  │ (Spec bounds) │          │ PDFs (EN/ES)  │          │ - Google Drive sync   │
  └───────┬───────┘          └───────────────┘          └───────────────────────┘
          │                                                         │
          └─────────────────────────────────────────────────────────┼──────┐
                                                                    ▼      ▼
                                                        ┌───────────────────────┐
                                                        │ Antigravity AI Skill  │
                                                        │ - CLI Drill Runner    │
                                                        │ - 4 Persona Drills    │
                                                        │ - Rubric Evaluation   │
                                                        └───────────────────────┘
```

---

## 3. Target Roles & Production CV Variants

`master_cv` generates and maintains four production targets across two dedicated engineering tracks:

| Track | Language | Canonical PDF File Path | Target Roles | Core Technical Stack |
|---|---|---|---|---|
| **Data Engineering** | English | `cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf` | Junior Data Engineer / Cloud Support Engineer (GCP) — US / Nearshore | Google Cloud Platform (BigQuery, Dataform, Datastream CDC), IBM InfoSphere DataStage, IBM DB2 LUW, PySpark, Python (PyArrow vectorization), PostgreSQL. |
| **Data Engineering** | Spanish | `cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.pdf` | Ingeniero de Datos Junior / Soporte Cloud GCP — LatAm / Regional | Mismo stack de datos con calibración CSS de alta densidad adaptada a la morfología sintáctica del español. |
| **AI & Publications** | English | `cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf` | AI Engineer / Machine Learning Researcher / Agentic SWE | OntoTab Paper (2nd author), Mini-Qwen3 from scratch in PyTorch, JEPA PoC on MNIST, Transformer architecture, XGBoost, Tabular ML. |
| **AI & Publications** | Spanish | `cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf` | Investigador en Inteligencia Artificial / Becas Internacionales | Mismo rigor experimental enfocado en acreditaciones académicas y comités evaluadores. |

---

## 4. The Truthfulness-as-Code Contract

To prevent resume inflation and ensure bulletproof defense during technical screens, all statements conform to the following non-negotiable boundaries:

1. **OntoTab Research Paper**:
   - Role: **Second Author** (AI Team Lead Joaquín Solórzano is 1st author).
   - Direct Leadership: Experimental activity `E01` (Raw and Numeric-Oracle Baselines).
   - Dataset & Scale: **30,000 credit records** from the UCI Taiwan Credit Default dataset.
   - Validation & Metrics: Nested 5×3 cross-validation with 2,000 bootstrap iterations. Top performance: **0.5596 Average Precision (AP)** with XGBoost.
   - Finding: Empirically proved that ontological text enrichment did not outperform clean tabular numeric features.
2. **GBM Professional Experience**:
   - Role: Digital Solutions Specialist Intern (Data & AI).
   - Duration: Exactly **13 weeks** (July 15, 2026 – October 14, 2026).
   - Scope: Authored enterprise near-real-time ELT architecture on GCP; built and backed up **15 integration jobs** in IBM InfoSphere DataStage; tuned IBM DB2 LUW on Red Hat Enterprise Linux.
3. **FERROSTATS Portfolio Project**:
   - Architecture: Cloud-Native Medallion Lakehouse on GCP (Datastream CDC → GCS Bronze → BigQuery/Dataform Silver/Gold → Dataproc Serverless).
   - Cost: Architected for **$0.00/month** cloud spend using GCP free-tier quotas and serverless execution.
4. **SQL Arena Platform**:
   - Scope: Local web application for SQL interview drills (React 19, Express, MySQL 8, Monaco Editor).
   - Solved Count: **3 / 34 problems solved** (`nulls-1`, `nulls-2`, `nulls-3`; currently working on `rounding-1`). Full 34-problem curriculum authored.
5. **English Proficiency**:
   - Certification: **EF SET C1 Advanced** with certified overall score **66 / 100** (issued Jan 10, 2026; Cert ID: `93nXaa`).
   - Breakdown: Listening 75 (C2 Proficient), Speaking 69 (C1 Advanced), Reading 67 (C1 Advanced), Writing 51 (B2 Upper Intermediate).
   - Strict Anti-Pattern: Never claiming 95/100 or general C2.
6. **Academic Status**:
   - **Instituto Nacional San Luis**: Bachillerato Técnico Vocacional en Desarrollo de Software, cumulative GPA **9.5 / 10.0**, graduation December 10, 2026.
   - **University of the People**: Bachelor of Science in Computer Science, formally admitted for Term 3 (commencing January 28, 2027), WSCUC accredited, 100% online.

---

## 5. Calibrated 1-Page CSS Geometry Engine

Spanish translations require 20–25% more character space than English. Under uncalibrated margins (`6.2mm 13.5mm; font-size: 9.1pt`), the Spanish Data Engineering CV overflows to 2 pages.

`master_cv` incorporates a battle-tested CSS geometry configuration:
```css
@page {
  size: letter;
  margin: 5.4mm 13.0mm 5.4mm 13.0mm;
  background: #ffffff;
  @bottom-right { content: none; }
}

body {
  font-family: 'Liberation Serif', 'Times New Roman', Times, Georgia, serif;
  font-size: 9.05pt;
  line-height: 1.14;
  color: #111827;
}

h2 {
  font-size: 10.8pt;
  line-height: 1.14;
  margin: 4.5px 0 1.5px 0;
  break-after: avoid;
}

/* WeasyPrint 70.0 ATS Fix: Eliminates orphaned bullet dots during copy/paste */
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

---

## 6. AI IDE Native Ecosystem Integration

`master_cv` is designed to be operated natively within modern AI development environments:

- **Antigravity**: Includes native skill `.agents/skills/cv-interview-defense/` allowing developers and agents to run interactive mock drills:
  ```bash
  python .agents/skills/cv-interview-defense/scripts/drill_runner.py --persona tech_lead --project gbm
  ```
- **Cursor**: Includes `.cursorrules` defining factual guardrails, preventing the LLM from adding unverified claims or modifying verified metrics when drafting cover letters or tailored profiles.
- **Windsurf**: Compatible with Cascade agent workflows for automated continuous integration.
- **Kiro**: Integrates formal verification specifications.

---

## 7. Quickstart & Developer Workflow

### Prerequisites
- **Python**: 3.12+
- **WeasyPrint**:
  - **Windows**: Install via Scoop: `scoop install weasyprint`
  - **Linux (Ubuntu/Debian)**: `sudo apt-get install -y libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 fonts-liberation`

### Setup
```bash
# Clone the repository
git clone https://github.com/bapatata688/master_cv.git
cd master_cv

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

### Build & Verification Commands
```bash
# Compile all 4 PDF targets
python scripts/compile_all.py

# Programmatically assert 1-page geometry and mediabox (612x792 pt)
python scripts/verify_geometry.py

# Run ethical truthfulness and metric validation linter
python scripts/lint_cv_truth.py

# Execute full local CI/CD verification harness
python scripts/run_ci_harness.py
```

---

## 8. Cryptographic Evidence & Primary Artifacts

All assertions in this portfolio are backed by verified primary documents stored in `evidence/`:

| Credential / Artifact | Evidence File Path | SHA256 Checksum | External Verification |
|---|---|---|---|
| **Google Cloud Associate Data Practitioner** | `evidence/certifications/Google_Cloud_Certified_Associate_Data_Practitioner.pdf` | `d1a4a3b987e0e1b06fd48c9966b330c5b1469f74ec7b0efc3931de4d4f7dc3a6` | Pearson VUE / Credly (Cert ID: `23e3584a246f4c149f26fea03cebcbbb`) |
| **EF SET C1 Advanced Certificate** | `evidence/certifications/EF_SET_Certificate_C1_Advanced.pdf` | `0cd51116d49a65e074c3aac8477bff2fa3e2725a499cff61a1319d1bed35ee92` | [cert.efset.org/93nXaa](https://cert.efset.org/93nXaa) |
| **GBM Letter of Recommendation (EN)** | `evidence/recommendations/Recommendation_Letter_Diego_Escobar_EN.docx` | `2356e0772336834bccb238435934cbd3a9663b9cf6224186ecb773a939a50eb1` | Official GBM endorsement (Joaquín Solórzano) |
| **GBM Carta de Recomendación (ES)** | `evidence/recommendations/Carta_Recomendacion_Diego_Escobar_ES.docx` | `f5bea59f283a575a622a79b18e7c0774babc3f5b9455715b30812b88024c71ed` | Official GBM endorsement (Joaquín Solórzano) |
| **OntoTab Scientific Manuscript** | `evidence/research/OntoTab-finaledit.pdf` | `b21838bc8f189f0984edfaafe7809a96b9412e962fc84b6d2417dbdfc989f983` | Co-author research artifact |

---

## 9. Engineering Hurdle & Decision Log Summary

Detailed rationale for architecture decisions is documented in `docs/DECISION_LOG.md`:
- **LOG-001: WeasyPrint Windows GTK DLL dlopen Resolution**: Adopted hybrid runner invoking Scoop CLI binary on Windows and native import in Linux CI.
- **LOG-002: Spanish CV 1-Page Calibrated CSS Margin Budget**: Calibrated vertical margins to `5.4mm` and font size to `9.05pt` to fit expanded verbatim UoPeople blocks.
- **LOG-003: WeasyPrint 70.0 ATS Orphaned Dot Extraction Fix**: Replaced standard list styles with `li::before` absolute-positioned bullets to ensure clean text copying in ATS parsers.
- **LOG-004: Google Drive Synchronized Dual Delivery**: Implemented atomic sync script placing canonical PDFs in portfolio root and timestamped snapshots in `CV_Prep`.

---

## 10. Contact & Professional Links

- **Diego Alejandro Escobar Barahona**
- **Location**: Soyapango, San Salvador, El Salvador
- **Email**: [diegoalejandroescobarahona1@gmail.com](mailto:diegoalejandroescobarahona1@gmail.com)
- **LinkedIn**: [linkedin.com/in/diego-escobar-dev](https://www.linkedin.com/in/diego-escobar-dev/)
- **GitHub**: [github.com/bapatata688](https://github.com/bapatata688)

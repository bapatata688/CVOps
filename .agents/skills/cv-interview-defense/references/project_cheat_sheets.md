# HOJAS DE REFERENCIA RÁPIDA POR PROYECTO (PROJECT CHEAT SHEETS)

Este documento compila los resúmenes técnicos condensados de cada proyecto para consulta rápida antes de una entrevista.

---

## 1. ONTOTAB (INVESTIGACIÓN CIENTÍFICA)
- **Título**: *"OntoTab: A Controlled Study of Ontology-Enriched Text for Tabular Credit Risk"*
- **Institución**: GBM (General Business Machines), San Salvador, El Salvador.
- **Rango del Candidato**: 2.º autor de 7 autores (coautor).
- **Liderazgo Técnico**: Líder de la Actividad Experimental E01 (Baselines estructurados y numéricos).
- **Primer Autor**: Joaquín Francisco Solórzano Corea (AI Team Lead en GBM).
- **Dataset**: UCI Default of Credit Card Clients (Taiwán) — **30,000** registros de crédito, 22.12% de mora.
- **Encoder**: `BAAI/bge-m3` congelado (*frozen*, d = 1,024 dimensiones) en inferencia pura sin fine-tuning.
- **Metodología**: Validación cruzada anidada **5×3**, 3 semillas pseudoaleatorias (`27092031`, `27092032`, `27092033`), **2,000** iteraciones de bootstrap estratificado pareado.
- **Métricas Clave**:
  - Baseline numérico R8 en XGBoost: **0.5596** AP (+12.2% sobre Regresión Logística 0.4981 AP).
  - Brazo ontológico verbalizado R5 en XGBoost: **0.5069** AP.
  - Contraste ontológico primario (R5 - R2E): -0.0063 AP (p < 0.05, degradación estadísticamente significativa).
  - Conclusión: Las variables numéricas limpias estructuradas superaron al texto denso enriquecido ontológicamente.

---

## 2. GBM (PASANTÍA PROFESIONAL)
- **Empresa**: GBM (General Business Machines) — Programa GBM2GROW.
- **Cargo**: Digital Solutions Specialist Intern (Data & AI).
- **Duración**: Exactamente **13 semanas** (15 de julio de 2026 – 15 de octubre de 2026).
- **Supervisores**: Joaquín Solórzano (AI Lead) y Juan Carlos Quintero (PO Data & AI).
- **Entregables**:
  - **15 jobs DataStage**: Pipelines ETL construidos en IBM InfoSphere DataStage (Transformers, Lookups, Joins, Merge, Funnel) con cero pérdida de datos.
  - **IBM DB2 LUW**: Consultas estructuradas y parameter tuning sobre Linux Red Hat Enterprise Linux (RHEL).
  - **Arquitectura ELT en GCP**: Co-diseño de propuesta cloud empresarial casi en tiempo real (BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage, HA VPN, IAM) con diagramas Lucidchart y DDL SQL en snake_case al 100% de especificaciones.
  - **Python CLI Tooling**: Herramienta de automatización bajo SDD con Kiro, acelerando compilación de documentación en -80% y resolviendo 24 tickets en Azure DevOps.

---

## 3. FERROSTATS (PORTAFOLIO CLOUD-NATIVE LAKEHOUSE)
- **Tipo**: Proyecto de portafolio personal de ingeniería de datos.
- **Repositorios**: `github.com/bapatata688/Ferrostats` y `github.com/b0ldm6diego`.
- **Arquitectura Medallion en Google Cloud Platform**:
  - *Bronze*: Ingesta de 4 tablas crudas a BigQuery vía APIs REST con latencia en el borde <50 ms y persistencia ACID local en SQLite (modo WAL).
  - *Silver*: Vistas staging en Google Dataform (SQLX) con aserciones automáticas de unicidad de PK e integridad referencial.
  - *Gold*: 3 Star Schema marts (`fct_daily_sales`, `mart_inventory_pareto_abc`, `dim_products`).
- **Analítica**: Segmentación Pareto ABC (80/20) con Window Functions, Burn Rate y Days of Inventory (DOI) con 15 días de buffer en Looker Studio (dashboard de 3 páginas).
- **FinOps**: **$0.00/mes** en GCP gracias a Cloud Run scale-to-zero (<3s cold start) y service accounts keyless.

---

## 4. SQL ARENA (PLATAFORMA DE ENTRENAMIENTO)
- **Stack**: React 19 + Vite + Tailwind CSS v4 + Monaco Editor en frontend; Express + MySQL 8.0 en backend.
- **Rol**: Creador y Arquitecto Full-Stack del 100% de la plataforma.
- **Hardening de Ingeniería**:
  - `ExecutionMutex`: Mutex en memoria que encola y serializa reinicios de sandbox para evitar contención en archivos `.ibd` de Windows NTFS.
  - Parser léxico AST: Inspección y bloqueo de inyecciones y multi-sentencias.
  - Driver `fields`: Inspección de paquetes crudos preservando esquemas con 0 filas.
- **Suite de Pruebas**: **136 tests** automatizados pasando al 100%.
- **Progreso de Usuario**: **3 de 34** resueltos (`nulls-1`, `nulls-2`, `nulls-3`, con `rounding-1` en curso).

---

## 5. EDUCACIÓN Y CERTIFICACIONES
- **University of the People**: B.S. in Computer Science (Pasadena, CA, acreditada por WSCUC, 100% Online). Admitido formalmente para Term 3, 2027 (inicio: 28 de enero de 2027).
- **EF SET English Certificate**: **66/100 (C1 Advanced)** emitido el 10/Ene/2026. Listening: **75/100 (C2 Proficient)**, Speaking: 69 (C1), Reading: 67 (C1), Writing: 51 (B2). Errata histórica "95/100" eliminada.
- **Google Cloud Certified**: Associate Data Practitioner (Pearson VUE / Credly, Cert ID: `23e3584a246f4c149f26fea03cebcbbb`).

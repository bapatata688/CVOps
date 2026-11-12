# ESPECIFICACIÓN Y SINCRONIZACIÓN EN LA NUBE: MANUAL DE DEFENSA EN ENTREVISTAS (CV_PREP 04)

## 1. GOBERNANZA DE SINCRONIZACIÓN EN GOOGLE WORKSPACE Y DRIVE

Este documento establece el mapeo oficial de sincronización bidireccional entre el repositorio local `master_cv` y el entorno de almacenamiento y gobernanza en la nube en Google Workspace.

### 1.1 Identificadores Oficiales de la Nube
- **Google Doc Maestro Central**: `Diego Escobar - Perfil Integral y Respaldo Operativo Central`  
  - Document ID: `16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ`  
  - URL: `https://docs.google.com/document/d/16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ/edit`  
  - Política de sincronización: Auditoría y actualización nocturna a las 11:00 PM UTC-6.
- **Google Drive — Raíz del Portafolio Profesional**:  
  - Carpeta: `Diego Escobar — CVs y Portafolio Profesional`  
  - Folder ID: `13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H`
- **Google Drive — Carpeta Específica de Preparación (`CV_Prep`)**:  
  - Carpeta: `📁 CV_Prep — Diego Escobar`  
  - Folder ID: `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb`  
  - URL: `https://drive.google.com/drive/folders/17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb`
- **Documento Destino Espejo en Google Docs**:  
  - Título en la Nube: `04_manual_defensa_entrevistas`  
  - Carpeta Contenedora: `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb`  
  - Archivo Fuente Local: `docs/INTERVIEW_DEFENSE_MANUAL.md`  
  - Herramienta de Sincronización: `gdocs` y `scripts/sync_drive.py`

---

## 2. CONTENIDO SINCRONIZADO: MANUAL DE DEFENSA TÉCNICA EN ENTREVISTAS

A continuación se transcribe de forma íntegra y sincronizada el manual maestro de defensa técnica para Diego Alejandro Escobar Barahona:

### 2.1 Resumen Ejecutivo de Proyectos y Anclas Fácticas
- **OntoTab**:
  - Investigación científica empírica sobre riesgo crediticio en GBM.
  - Dataset: UCI Taiwán con **30,000** registros de crédito (22.12% de mora).
  - Protocolo estadístico: Validación cruzada anidada **5×3** y **2,000** iteraciones de bootstrap estratificado pareado.
  - Encoder: `BAAI/bge-m3` congelado (1,024 dimensiones) sin fine-tuning.
  - Resultado: Baseline numérico R8 en XGBoost liderado por Diego alcanzó **0.5596** AP frente a 0.5069 AP del brazo ontológico verbalizado R5.
  - Rango de autoría: **2.º autor de 7** autores; líder de la Actividad Experimental E01.
  - Primer autor e Investigador Principal: Joaquín Francisco Solórzano Corea (AI Team Lead en GBM).
- **GBM (General Business Machines)**:
  - Duración de pasantía: **13 semanas** continuas (15 de julio de 2026 – 15 de octubre de 2026).
  - Cargo: Digital Solutions Specialist Intern (Data & AI) en el programa GBM2GROW.
  - Entregables: **15 jobs DataStage** empresariales desarrollados y verificados con cero pérdida de datos; administración de **IBM DB2 LUW sobre Red Hat Enterprise Linux (RHEL)**; propuesta de arquitectura ELT empresarial en Google Cloud Platform (BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage, HA VPN); herramienta CLI de automatización bajo SDD con -80% en tiempo de compilación.
- **FERROSTATS**:
  - Lakehouse Medallion Cloud-Native en Google Cloud Platform con streaming transaccional desacoplado POS.
  - Latencia en el borde <50 ms mediante base local SQLite en modo WAL y APIs REST hacia BigQuery Bronze.
  - Aserciones automatizadas de calidad de datos en Google Dataform (SQLX).
  - 3 Star Schema data marts en capa Gold con analítica Pareto ABC (80/20), Burn Rate y Days of Inventory (DOI) con 15 días de buffer.
  - FinOps: Costo operativo verificado de **$0.00/mes** en GCP gracias a Cloud Run scale-to-zero e identidades keyless de IAM.
- **SQL Arena**:
  - Plataforma web interactiva local de entrenamiento técnico en SQL.
  - Creador y Arquitecto Full-Stack (React 19 + Monaco Editor + Express + MySQL 8.0).
  - Resiliencia: `ExecutionMutex` asíncrono para eliminar la contención de bloqueos de archivos InnoDB (`.ibd`) en Windows NTFS.
  - Seguridad: Parser léxico que bloquea inyecciones SQL y multi-statements.
  - Inspección de paquetes crudos `fields` para preservar esquemas en resultados de 0 filas.
  - Calidad de software: Suite de **136 tests** automatizados pasando al 100%.
  - Honestidad de candidato: Progreso de estudiante de **3 de 34** problemas resueltos (`nulls-1`, `nulls-2`, `nulls-3`, con `rounding-1` en curso).
- **Educación y Certificaciones**:
  - University of the People: Bachelor of Science in Computer Science, Pasadena, CA (acreditada por WSCUC, 100% Online). Admitido formalmente para Term 3, 2027 (inicio: 28 de enero de 2027).
  - EF SET Certificate: Calificación oficial certificada de **66/100 (C1 Advanced)** con **75/100 en Listening (C2 Proficient)**, retirando de forma definitiva la errata preliminar de borrador "95/100".
  - Google Cloud Certified Associate Data Practitioner (Cert ID: `23e3584a246f4c149f26fea03cebcbbb`).

---

## 3. SCRIPTS STAR POR PERSONA DE EVALUACIÓN

El manual contempla respuestas directas en formato STAR para cuatro tipos de evaluadores:
- **Recruiter**: Trayectoria, pasantía de 13 semanas en GBM, fluidez en inglés C1/C2, y transición hacia roles de Junior Data Engineer o Cloud Support Engineer en GCP.
- **Tech Lead**: Decisiones de diseño en FERROSTATS ($0.00/mes, latencia <50 ms), resolución de contención NTFS en SQL Arena vía ExecutionMutex, y diseño de los 15 jobs DataStage con DB2 en RHEL.
- **ML Researcher**: Análisis de los 30,000 registros en OntoTab, validación anidada 5×3, 2,000 bootstraps, métrica de 0.5596 AP, y fundamentos estadísticos de por qué el texto denso degradó el rendimiento frente a las variables numéricas directas.
- **Auditor**: Protocolo de verificación forense, procedencia de autoría (2.º de 7), disolución del error histórico 95/100 en favor del 66/100 real, y distinción estricta entre arquitecto de SQL Arena (136 tests) y usuario estudiante (3/34 resueltos).

---

## 4. REGISTRO DE SINCRONIZACIÓN Y ACCESO CLOUD

| Artefacto Local | Destino en Google Drive | Folder ID | Doc ID / Target | Estado de Sincronización |
|---|---|---|---|---|
| `docs/INTERVIEW_DEFENSE_MANUAL.md` | `📁 CV_Prep — Diego Escobar` | `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb` | `04_manual_defensa_entrevistas` | Mapeado y Verificado |
| `resources/evidence_matrix.json` | `📁 CV_Prep — Diego Escobar` | `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb` | `evidence_matrix_backup.json` | Mapeado y Verificado |
| Perfil Maestro Central | Carpeta Raíz Portafolio | `13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H` | `16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ` | Sincronizado |

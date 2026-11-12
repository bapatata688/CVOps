# MATRICES DE ADAPTACIÓN Y PARÁFRASIS ATS POR ROL OBJETIVO

## 1. PRINCIPIOS DE PARÁFRASIS LEGÍTIMA Y CUMPLIMIENTO ATS

### 1.1 El Reto de Optimización para Sistemas de Seguimiento de Candidatos (ATS)
Los sistemas modernos de seguimiento de candidatos (*Applicant Tracking Systems* o ATS como Workday, Greenhouse, Lever, iCIMS y Taleo) analizan los currículums vitae mediante analizadores léxicos (*parsers*) que extraen entidades, calculan similitudes semánticas vectoriales y puntúan la densidad de palabras clave técnicas (*keyword match scores*) requeridas en las descripciones de empleo.

Para candidatos en etapas tempranas de su carrera profesional, existe la tentación recurrente de inflar títulos o incluir tecnologías que solo se conocen superficialmente (*vibecoding* o relleno de palabras clave). En el marco `master_cv`, adoptamos el enfoque opuesto: **Paráfrasis Legítima de Alta Densidad**.

### 1.2 Definición Operativa: Paráfrasis Legítima vs Inflación de Responsabilidades
- **Paráfrasis Legítima (Aprobada)**: Consiste en articular una tarea o entregable técnico genuinamente ejecutado utilizando la terminología estándar y los modismos precisos que la industria y los algoritmos ATS demandan para un rol específico. Si Diego diseñó vistas en Dataform con reglas de unicidad y no-nulidad, esto puede describirse legítimamente como *"Data Quality Assertions"* para un rol de Data Engineer, o como *"Data Contracts under Spec-Driven Development"* para un rol de Analytics Engineer. Ambos ángulos describen la misma verdad empírica con el vocabulario idóneo.
- **Inflación de Responsabilidades (Estrictamente Prohibida)**: Ocurre cuando se altera la naturaleza del trabajo, se reclama la autoría exclusiva de tareas ejecutadas en equipo, se utilizan títulos superiores a los ostentados (e.g. autodenominarse "Senior" o "Lead"), o se incluyen tecnologías que no forman parte de los artefactos verificables del candidato.

---

## 2. MATRIZ DE ROL 1: JUNIOR / INTERN DATA ENGINEER

### 2.1 Perfil y Segmento de Mercado Objetivo
- **Denominaciones del Puesto**: Junior Data Engineer, Associate Data Engineer, Cloud Data Engineer, ETL Developer.
- **Rango Salarial Objetivo**: $1,500 – $2,500 USD / mes (Empresas de software Nearshore en EE. UU. / LatAm) o $1,750 USD / mes en soporte técnico cloud empresarial (TELUS International GCP Support).
- **Competencias Técnicas Evaluadas por ATS**:
  - `ELT / ETL Pipelines` & `CDC (Change Data Capture)`
  - `Google BigQuery` & `Google Dataform (SQLX)`
  - `Medallion Lakehouse Architecture (Bronze / Silver / Gold)`
  - `Data Quality Assertions & Integrity Constraints`
  - `IBM InfoSphere DataStage (Enterprise ETL)`
  - `Relational Databases (PostgreSQL 18, MySQL 8, IBM DB2 LUW on Linux RHEL)`
  - `SQL Avanzado (Window Functions, CTEs recursivas, ACID Isolation)`
  - `Cloud Governance, IAM Least-Privilege & FinOps ($0.00/mo architecture)`

### 2.2 Viñetas de Experiencia Aprobadas (Inglés y Español)

#### Proyecto GBM (Pasantía Profesional)
- **ELT en Google Cloud**:
  - **EN**: *"Co-designed enterprise near-real-time ELT pipeline on Google Cloud (BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage, HA VPN, Cloud Router) delivering dimensional Lucidchart models and snake_case DDL SQL scripts meeting 100% of client specs."*
  - **ES**: *"Co-diseñó arquitectura de modernización ELT casi en tiempo real en GCP (BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage, HA VPN) entregando modelos dimensionales en Lucidchart y scripts DDL SQL en snake_case al 100% de especificaciones."*
- **IBM DataStage & DB2 en Linux**:
  - **EN**: *"Developed, parameterized, and tested 15 enterprise ETL jobs in IBM InfoSphere DataStage (Transformers, Lookups, Joins, Merge, Funnel) with zero data loss, querying and configuring IBM DB2 LUW instances on Linux RHEL."*
  - **ES**: *"Desarrolló, parametrizó y validó 15 jobs de integración ETL en IBM InfoSphere DataStage (Transformers, Lookups, Joins, Merge, Funnel) con cero pérdida de datos, consultando y configurando instancias IBM DB2 LUW sobre Linux RHEL."*
- **Gobernanza Cloud y FinOps**:
  - **EN**: *"Established auditable cloud governance and FinOps budget validation for client proposals by co-authoring GCP security frameworks (least-privilege IAM, Service Accounts, audit logging, data lineage) and modeling costs in Google Cloud Pricing Calculator."*
  - **ES**: *"Estableció gobernanza cloud y validación FinOps para propuestas de clientes co-diseñando marcos de seguridad GCP (IAM de mínimo privilegio, Service Accounts, auditoría, linaje) y modelando costos en Google Cloud Pricing Calculator."*

#### Proyecto FERROSTATS (Lakehouse Medallion Cloud-Native)
- **Arquitectura Medallion en BigQuery + Dataform**:
  - **EN**: *"Architected cloud-native Medallion Lakehouse (Bronze/Silver/Gold) on Google BigQuery orchestrated via Dataform SQLX, transforming 7 raw landing tables into curated Silver views with automated assertions and 3 Gold Star Schema marts."*
  - **ES**: *"Diseñó Lakehouse Medallion Cloud-Native (Bronze/Silver/Gold) en Google BigQuery orquestado con Dataform SQLX, transformando tablas crudas en vistas Silver con aserciones automatizadas de calidad y 3 data marts en Star Schema."*
- **Streaming de Ingesta y FinOps**:
  - **EN**: *"Engineered decoupled OLTP-to-OLAP streaming pipeline achieving <50 ms edge latency into BigQuery Bronze via REST APIs, enforcing strict ACID concurrency constraints while maintaining a permanent $0.00/mo GCP architecture via Cloud Run scale-to-zero."*
  - **ES**: *"Implementó pipeline desacoplado OLTP-a-OLAP con latencia <50 ms hacia BigQuery Bronze vía APIs REST, garantizando transacciones ACID y arquitectura FinOps permanente de $0.00/mes en GCP mediante Cloud Run scale-to-zero."*

#### Proyecto SQL Arena (Ingeniería de Aislamiento en Bases de Datos)
- **Resiliencia de Sandbox y Concurrencia**:
  - **EN**: *"Engineered isolated MySQL 8 execution harness featuring an asynchronous in-memory mutex serializing database resets to eliminate Windows NTFS file lock collisions, backed by raw driver packet inspection preserving zero-row schemas."*
  - **ES**: *"Diseñó motor de ejecución aislado en MySQL 8 con mutex asíncrono en memoria para serializar reinicios de sandbox y eliminar contención NTFS en Windows, preservando esquemas de 0 filas mediante inspección cruda de paquetes de driver."*

---

## 3. MATRIZ DE ROL 2: JUNIOR / INTERN DATA ANALYST & ANALYTICS ENGINEER

### 3.1 Perfil y Segmento de Mercado Objetivo
- **Denominaciones del Puesto**: Junior Data Analyst, Analytics Engineer, Business Intelligence (BI) Developer, Junior Analytics Consultant.
- **Rango Salarial Objetivo**: $1,500 – $2,200 USD / mes (Mercado remoto internacional).
- **Competencias Técnicas Evaluadas por ATS**:
  - `Analytics Engineering` & `dbt / Dataform Modeling`
  - `Dimensional Modeling (Kimball Star Schema, Facts & Dimensions)`
  - `Executive BI Dashboards (Looker Studio, Tableau, Power BI)`
  - `SQL Analytics (Window Functions, Aggregations, Rolling Metrics)`
  - `Inventory Analytics (Pareto ABC 80/20, Burn Rate, Days of Inventory - DOI)`
  - `Data Contracts & Automated Data Quality Assertions`
  - `Statistical Evaluation & Distribution Metrics`

### 3.2 Viñetas de Experiencia Aprobadas (Inglés y Español)

#### Proyecto FERROSTATS (Analítica de Inventarios y BI)
- **Lógica de Negocio y Segmentación Pareto ABC**:
  - **EN**: *"Formulated functional data contracts under Spec-Driven Development (SDD) for 80/20 Pareto ABC inventory segmentation, Daily Burn Rate, and Days of Inventory (DOI) with 15-day safety buffers, executing analytical SQL window functions to power a 3-page Looker Studio executive dashboard."*
  - **ES**: *"Diseñó contratos de datos analíticos para clasificación Pareto ABC 80/20, Burn Rate diario y Días de Inventario (DOI) con buffer de seguridad de 15 días, implementando Window Functions en SQL para alimentar un dashboard de 3 páginas en Looker Studio."*
- **Aserciones Automatizadas de Calidad en Dataform**:
  - **EN**: *"Configured automated data quality assertion suites in Google Dataform (SQLX) enforcing primary key uniqueness, referential integrity, and non-null constraints across Silver layers prior to analytical mart aggregation."*
  - **ES**: *"Configuró suites automatizadas de aserciones de calidad en Google Dataform (SQLX) validando unicidad de claves primarias, integridad referencial y restricciones no nulas en capas Silver antes de la agregación de marts."*

#### Investigación OntoTab (Analítica Empírica y Modelado Predictivo)
- **Evaluación Estadística y Curvas de Precisión**:
  - **EN**: *"Evaluated predictive risk patterns across 30,000 credit records, computing seed-averaged out-of-fold probability distributions and Average Precision (0.5596 AP on XGBoost) using 5x3 nested cross-validation and paired bootstrap confidence intervals."*
  - **ES**: *"Analizó patrones predictivos de riesgo sobre 30,000 registros crediticios, calculando distribuciones de probabilidad out-of-fold y Average Precision (0.5596 AP en XGBoost) bajo validación anidada 5x3 e intervalos bootstrap pareados."*

#### Proyecto GBM (Modelado Dimensional para Almacén de Datos)
- **Modelado Dimensional en Lucidchart**:
  - **EN**: *"Transformed client operational data into dimensional warehouse schemas, producing clean entity-relationship models in Lucidchart and validating data completeness across 15 enterprise ETL pipelines with zero loss."*
  - **ES**: *"Modeló datos operacionales en esquemas dimensionales de data warehouse en Lucidchart y validó completitud de datos a lo largo de 15 pipelines ETL empresariales con cero pérdida."*

---

## 4. MATRIZ DE ROL 3: JUNIOR / TRAINEE AI & AGENTIC SOFTWARE ENGINEER

### 4.1 Perfil y Segmento de Mercado Objetivo
- **Denominaciones del Puesto**: Trainee Agentic Software Engineer (Ravn Nerdery Program), Junior AI Engineer, Junior Python Software Engineer.
- **Rango Salarial Objetivo**: $1,200 – $1,800+ USD / mes.
- **Competencias Técnicas Evaluadas por ATS**:
  - `Agentic Engineering & LLM Systems`
  - `Python Tooling & Spec-Driven Development (SDD)`
  - `Git / SSH Collaborative Workflows & CI/CD Pipelines`
  - `Transformer Architecture Fundamentals (RMSNorm, RoPE, SwiGLU)`
  - `Vector Embeddings & Frozen Model Evaluation (BGE-M3)`
  - `Full-Stack Development (TypeScript, Node.js, Express, React 19)`
  - `Automated Unit & Regression Testing Suites`

### 4.2 Viñetas de Experiencia Aprobadas (Inglés y Español)

#### Investigación OntoTab (Machine Learning Empírico)
- **Evaluación Rigurosa de Embeddings y Modelos Tabulares**:
  - **EN**: *"Led baseline machine learning experiments (Activity E01) over 30,000 credit records (UCI Taiwan) using 5x3 stratified nested cross-validation and 2,000 bootstrap iterations; evaluated frozen BGE-M3 embeddings vs tabular features, proving structured numeric channels achieve 0.5596 AP (+12.2% over Logistic Regression)."*
  - **ES**: *"Lideró experimentos de línea base (Actividad E01) sobre 30,000 registros de crédito (UCI Taiwán) con validación anidada 5x3 y 2,000 bootstraps; evaluó embeddings congelados de BGE-M3 frente a variables tabulares, demostrando que canales numéricos alcanzan 0.5596 AP (+12.2% sobre Regresión Logística)."*

#### Proyecto GBM (Herramientas CLI y SDD)
- **Herramienta CLI en Python y Flujos de Ingeniería**:
  - **EN**: *"Built a Python CLI automation tool under Spec-Driven Development (SDD), accelerating corporate technical documentation compile time by 80% and resolving 24+ Azure DevOps engineering tickets while mentoring peers on Git/SSH workflows."*
  - **ES**: *"Desarrolló herramienta CLI en Python bajo Spec-Driven Development (SDD), acelerando compilación de documentación técnica en un 80% y resolviendo 24+ tickets en Azure DevOps mientras capacitaba al equipo en Git/SSH."*

#### Deep Learning: Mini-Qwen3
- **Implementación Modular de Transformers**:
  - **EN**: *"Engineered modular PyTorch (nn.Module) and Excel implementation of Mini-Qwen3 Transformer (RMSNorm, QK-Norm, RoPE, causal attention, SwiGLU) with automated regression tests verifying exact mathematical parity."*
  - **ES**: *"Implementó arquitectura modular de Mini-Qwen3 Transformer en PyTorch (nn.Module) y Excel (RMSNorm, QK-Norm, RoPE, causal attention, SwiGLU) con tests de regresión verificando paridad matemática exacta."*

#### Proyecto SQL Arena (Ingeniería de Software Full-Stack)
- **Plataforma Interactiva y Sandbox Aislado**:
  - **EN**: *"Architected and built full-stack SQL evaluation platform (React 19, Monaco Editor, Express, MySQL 8) featuring an in-memory execution mutex serializing sandbox resets, lexical AST parser blocking SQL injection, and a 136-test regression suite."*
  - **ES**: *"Arquitectó y construyó plataforma full-stack de evaluación SQL (React 19, Monaco Editor, Express, MySQL 8) con mutex en memoria para serializar reinicios de sandbox, parser léxico AST anti-inyecciones y suite de 136 tests de regresión."*

---

## 5. LISTA NEGRA DE PALABRAS INFLADAS Y SUSTITUTOS DE RIGOR

La siguiente tabla define los términos prohibidos por el arnés de contención, el riesgo técnico asociado en una entrevista y los sustitutos verificables aprobados que maximizan la conversión sin exponer al candidato:

| Término Inflado / Prohibido | Riesgo en Entrevista Técnica | Sustituto Técnico Verificable Aprobado |
|:---|:---|:---|
| *"Senior Data Engineer"* o *"Staff Engineer"* | Cuestionamiento inmediato de años de experiencia; el entrevistador asumirá falsedad al cotejar fecha de nacimiento (2007) y pasantía en 2026. | **"Junior Data Engineer"** o **"Data Engineer Intern (Digital Solutions Specialist)"**. |
| *"Machine Learning Engineer"* (aplicado a OntoTab) | Preguntas teóricas sobre despliegue de modelos en Kubernetes o Triton Server que no correspondieron al estudio. | **"Co-author & ML Researcher | OntoTab"** o **"Líder de Actividad Experimental E01"**. |
| *"Lead Author / Primer Autor"* | El examinador abrirá el PDF de OntoTab y constatará que el primer autor es Joaquín Solórzano. Descalificación por fraude. | **"Co-author (2nd author of 7)"** o **"Coautor (2.º de 7)"**. |
| *"Published in IEEE / ACM"* | Solicitud del DOI o enlace en IEEE Xplore; su ausencia invalidará el proceso de selección. | **"Internal Scientific Research Manuscript at GBM"** (manuscrito empírico de 16 páginas). |
| *"EF SET 95/100"* | Discrepancia directa contra el certificado oficial que marca 66/100 C1. | **"EF SET English Certificate — C1 Advanced (66/100, Listening 75/100 C2 Proficient)"**. |
| *"Completed 34/34 exercises on SQL Arena"* | El entrevistador puede solicitar demostración en vivo de soluciones avanzadas en el sandbox. | **"Platform Architect & Creator (34 exercises designed, 136 automated tests, 3/34 solved in user telemetry)"**. |
| *"Revenue-generating startup / USD 5,000 MRR"* | Solicitud de estados financieros o balances tributarios de la empresa. | **"Cloud-Native Medallion Lakehouse Portfolio Project (USD 0.00/mo FinOps architecture on GCP)"**. |
| *"Production PySpark Distributed Cluster"* | Indagación sobre tuning de memoria en clústeres Spark, GC pauses y balanceo de particiones en prod. | **"BigQuery orchestrated via Dataform SQLX with planned batch PySpark roadmap"**. |

---

## 6. MAPEO DE COMPATIBILIDAD CON SISTEMAS ATS (WORKDAY, GREENHOUSE, LEVER)

Para garantizar un puntaje de extracción (*parsing score*) superior al 95% en los motores ATS más exigentes del mercado, las plantillas generadas en `master_cv` deben acatar los siguientes principios de maquetación:

1. **Jerarquía Semántica Limpia**:
   - Encabezados claros (`<h1>` para el nombre, `<h2>` para las secciones principales: *Professional Experience*, *Technical Projects*, *Education*, *Certifications*).
   - Uso de viñetas estándar `<ul>`/`<li>` en lugar de iconos decorativos o caracteres exóticos que confunden a los motores OCR y tokenizadores.
2. **Dualidad Acrónimo-Expansión**:
   - Cada tecnología relevante debe mencionarse tanto con su nombre completo como con su sigla estándar al menos una vez en el documento (ejemplo: *"Extract, Load, Transform (ELT)"* y *"ELT"*, *"Change Data Capture (CDC)"* y *"CDC"*).
3. **Estructura Monocolumna para Datos Críticos**:
   - Los datos de contacto, enlaces a perfiles (LinkedIn, GitHub) y fechas deben residir en flujo vertical estándar, evitando tablas complejas o cajas flotantes que provocan que los motores ATS mezclen los nombres de empresas con las instituciones educativas.
4. **Calibración de Tipografía y Márgenes para Compactación sin Desbordamiento**:
   - Para las versiones en español (cuya expansión léxica típica es del 15% al 20% respecto al inglés), se establece el estándar tipográfico:
     - Márgenes de página: `@page { margin: 5.4mm 13.0mm; }`
     - Tamaño de fuente base: `body { font-size: 9.05pt; }`
     - Interlineado estricto: `line-height: 1.18;`
   - Esto garantiza que las descripciones densas y los bloques verbatim de University of the People se mantengan con rigor visual dentro del límite estricto de **1 página**.

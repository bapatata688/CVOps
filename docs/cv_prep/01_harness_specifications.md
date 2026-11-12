# ESPECIFICACIONES FORMALES Y HARNESS DE CONTENCIÓN ÉTICA (MASTER_CV)

## 1. PROPÓSITO DEL HARNESS Y DIRECTIVA DE GOBERNANZA

### 1.1 Filosofía de Veracidad Radical y Tolerancia Cero a la Inflación
El marco `master_cv` está fundamentado en el principio inquebrantable de **veracidad comprobable al 100%**. En el mercado técnico global contemporáneo, los procesos de debida diligencia (*background checks* forenses, validaciones de credenciales Pearson VUE, cotejo de repositorios y escrutinio en entrevistas técnicas de arquitectura) detectan y penalizan severamente cualquier discrepancia entre lo afirmado en el currículum vitae y la realidad fáctica comprobable.

Este arnés ético de contención define las fronteras innegociables para cada responsabilidad, métrica de rendimiento, certificación oficial y rol profesional de Diego Alejandro Escobar Barahona. La política operativa es de **cero tolerancia a la inflación de responsabilidades**: es preferible documentar un rol junior o de pasantía respaldado por hechos de ingeniería verificables y métricas reproducibles, que un título inflado que colapse bajo escrutinio técnico en entrevistas FAANG o revisiones corporativas.

### 1.2 Directiva Oficial de Gobernanza y Sincronización en la Nube
El presente documento constituye la especificación canónica humana y está sincronizado de manera bidireccional con el ecosistema de gobernanza técnica en Google Workspace:
- **Google Doc Maestro Central**: `Diego Escobar - Perfil Integral y Respaldo Operativo Central` (ID: `16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ`).
- **Google Drive de Portafolio Profesional**: Carpeta oficial `📁 CV_Prep — Diego Escobar` ubicada dentro de la raíz del portafolio `Diego Escobar — CVs y Portafolio Profesional` (ID: `13rrJG0S0yLlk5H5ieeGkNM0Yy3XCdN7H`).
- **Arnés de Validación Automatizada**: Consumido por el linter ético de Milestone 4 (`scripts/lint_cv_truth.py`) mediante el archivo canónico estructurado `master_cv/resources/evidence_matrix.json`.

Toda afirmación, viñeta (*bullet point*), métrica cuantitativa o título profesional que aspire a incorporarse a las plantillas de producción en `cv/` debe contar con un respaldo primario explícito en este arnés antes de autorizarse su compilación o despliegue.

### 1.3 Regla de Oro de Procedencia de Evidencia
Todo elemento descriptivo o cuantitativo presente en el CV debe mapear de manera unívoca a uno de los siguientes artefactos primarios comprobables:
1. **Credenciales Oficiales Emitidas por Terceros**: PDFs firmados y certificados con identificadores unívocos verificables en línea (Pearson VUE, Credly, EF SET).
2. **Manuscritos Científicos y Benchmarks Experimentales**: Documentos técnicos fechados con autoría formal, tablas de resultados empíricos, semillas pseudoaleatorias e intervalos de confianza reproducibles (`OntoTab-finaledit.pdf`).
3. **Cartas Institucionales y Avales de Supervisión**: Documentos corporativos y testimonios públicos verificables de supervisores directos en plataformas profesionales (LinkedIn, constancias de pasantía GBM2GROW).
4. **Repositorios de Código y Suites de Calidad**: Repositorios de software con historial de commits inmutable, contratos de datos explícitos y suites de pruebas automatizadas con 100% de aserciones pasando (`sql-arena`, `Ferrostats`).

---

## 2. ESPECIFICACIÓN FORMAL Y LÍMITES POR DOMINIO

### 2.1 Investigación Científica: OntoTab

#### Contexto y Artefacto Primario
- **Artefacto Primario**: `c:\Users\Usuario\Projects\coe\research\ontotab\OntoTab-finaledit.pdf` (16 páginas, SHA256: `910df9f04eab...`).
- **Título Oficial**: *"OntoTab: A Controlled Study of Ontology-Enriched Text for Tabular Credit Risk"*.
- **Filiación Institucional**: GBM (General Business Machines), San Salvador, El Salvador.
- **Naturaleza del Documento**: Manuscrito de investigación científica interna en GBM. Joaquín Francisco Solórzano Corea (Product Owner y AI Team Lead en GBM) otorgó autorización formal el 09 de noviembre de 2026 para compartir el PDF íntegro en postulaciones laborales y convocatorias de becas internacionales.

#### Autoría y Rol Específico
- **Rango de Autoría Formal**: **2.º autor de 7 autores listados** (`descobar@gbm.net`). Primer autor y Lead Researcher: Joaquín Francisco Solórzano Corea (`jsolorzano@gbm.net`). Coautores: Daniella Navarro, Beatriz Beltrán, Gerardo Quintanilla, Edwin Fernandez, Luis Escobar.
- **Rol Técnico de Diego**: **Líder de la Actividad Experimental E01** (Líneas base Raw y Numeric-Oracle: brazos de evaluación R0 y R8 sobre Regresión Logística, XGBoost y Perceptrón Multicapa / MLP).

#### Dataset, Metodología y Parámetros Numéricos Verificados
- **Dataset**: UCI Default of Credit Card Clients (Taiwán) — **30,000 registros de crédito** con una tasa positiva de incumplimiento (*default rate*) del **22.12%**.
- **Arquitectura de Codificación**: Modelo de embeddings `BAAI/bge-m3` congelado (*frozen*, dimensión d = 1,024), evaluado en inferencia pura sin fine-tuning para verbalizaciones ontológicas.
- **Protocolo Estadístico y Validación**: Validación cruzada anidada estratificada **5×3** (5 pliegues exteriores con 6,000 registros de prueba cada uno; 3 pliegues interiores sobre 24,000 registros para optimización de hiperparámetros). Tres semillas pseudoaleatorias reproducibles: `27092031`, `27092032`, `27092033`. **2,000 iteraciones de bootstrap estratificado pareado** para estimación no paramétrica de intervalos de confianza al 95%.
- **Métricas Empíricas Clave (Tabla 4 y Tabla 5 del Paper)**:
  - Baseline numérico R8 en XGBoost (liderado por Diego): **0.5596 AP** (exacto: `0.559596`) frente a Regresión Logística (0.4981 AP), representando una ganancia de **+12.2%**.
  - Baseline estructurado crudo R0 en XGBoost: **0.5589 AP** (exacto: `0.558879`).
  - Brazo de texto ontológico verbalizado R5 en XGBoost: **0.5069 AP** (exacto: `0.506909`).
  - Brazo híbrido texto + numérico R9 en XGBoost: **0.5568 AP** (exacto: `0.556833`).
  - Contraste primario ontológico (R5 - R2E): **-0.0063 AP** [-0.0101, -0.0022] (*degradación estadísticamente significativa causada por la verbalización textual frente al control neutro*).
  - Restauración híbrida (R9 - R5): **+0.0499 AP** [+0.0432, +0.0566].
  - Contraste híbrido vs numérico (R9 - R8): **-0.0028 AP** [-0.0067, +0.0014] (*el intervalo cruza el cero, demostrando empíricamente que agregar texto enriquecido con ontologías no añade ganancia marginal sobre las variables numéricas estructuradas limpias*).

#### Límites de Contención Ética
- ✅ **PERMITIDO**:
  - Declararse "Coautor (2.º autor de 7)" de la investigación empírica OntoTab en GBM.
  - Declarar el liderazgo de la Actividad Experimental E01 (diseño, ejecución y evaluación de baselines R0 y R8 sobre 30,000 registros).
  - Citar métricas exactas: 0.5596 AP en XGBoost, validación anidada 5×3 y 2,000 bootstraps.
  - Indicar que el manuscrito formal de 16 páginas está autorizado por el autor principal para revisión técnica.
- ❌ **ESTRICTAMENTE PROHIBIDO**:
  - Auto-denominarse "Machine Learning Engineer" o "Investigador Principal / Principal Investigator" a raíz de este proyecto.
  - Omitir la posición de autoría o sugerir que fue el autor líder o único autor.
  - Afirmar que el artículo fue publicado en conferencias arbitradas (IEEE, ACM, NeurIPS, ICML, KDD) o revistas indexadas por pares (es un manuscrito de investigación corporativa interna).
  - Atribuirse el diseño o liderazgo de las ramas ontológicas OWL/RDF o verbalizaciones R3, R4, R5 (fueron desarrolladas por otros miembros del equipo).

---

### 2.2 Experiencia Profesional: GBM (General Business Machines)

#### Contexto y Artefactos Primarios
- **Artefactos Primarios**:
  - Carta de recomendación oficial: `c:\Users\Usuario\Projects\coe\recommendations/en/Recommendation_Letter_Diego_Escobar_EN.docx`.
  - Carta en español: `c:\Users\Usuario\Projects\coe\recommendations/es/Carta_Recomendacion_Diego_Escobar_ES.docx`.
  - Respaldo público verificado en LinkedIn de Juan Carlos Quintero Escobar (Product Owner Data & AI en GBM, supervisor directo).
- **Cargo Oficial**: **Digital Solutions Specialist Intern (Data & AI)** dentro del programa corporativo GBM2GROW en San Salvador, El Salvador.
- **Fechas Exactas**: **15 de julio de 2026 – 15 de octubre de 2026** (exactamente **13 semanas**).

#### Entregables Técnicos Verificados
1. **Propuesta de Arquitectura ELT en GCP**: Co-diseñó una arquitectura ELT empresarial casi en tiempo real sobre Google Cloud Platform (BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage, HA VPN, Cloud Router, IAM) entregando diagramas dimensionales en Lucidchart y scripts SQL DDL en nomenclatura `snake_case` cumpliendo el 100% de especificaciones de cliente.
2. **Integración Empresarial ETL en IBM InfoSphere DataStage**: Creó, parametrizó y validó **15 jobs de integración de datos en DataStage** (utilizando Transformers, Lookups, Joins, Merge, Funnel, tratamiento de valores nulos y reglas de transformación de negocio) asegurando cero pérdida de datos.
3. **Administración y Consultas en Bases de Datos Relacionales**: Parametrizó y ejecutó consultas estructuradas sobre **IBM DB2 LUW montado en Red Hat Enterprise Linux (RHEL)**.
4. **Gobernanza Cloud y FinOps**: Coautor de marcos de seguridad y gobernanza en la nube (IAM de mínimo privilegio, Service Accounts dedicadas, auditoría, linaje de datos) y dimensionamiento presupuestario en Google Cloud Pricing Calculator.
5. **Automatización CLI bajo SDD**: Diseñó e implementó una herramienta CLI en Python bajo Spec-Driven Development (SDD), reduciendo el tiempo de compilación de documentación técnica en un **80%** y resolviendo más de **24 ítems de trabajo en Azure DevOps**.
6. **Investigación Deep Learning (Mini-Qwen3)**: Diseñó e implementó la arquitectura modular de Mini-Qwen3 Transformer desde cero en PyTorch (`nn.Module`) y Excel (RMSNorm, QK-Norm, RoPE, atención causal, SwiGLU, weight tying) con paridad matemática demostrada mediante pruebas de regresión automatizadas.

#### Límites de Contención Ética
- ✅ **PERMITIDO**:
  - Declarar el cargo exacto de pasantía / intern: "Digital Solutions Specialist Intern (Data & AI)" o "Data Engineer Intern".
  - Describir con rigor los 15 jobs en IBM DataStage, la administración de DB2 en RHEL y el co-diseño de la propuesta ELT en GCP.
  - Mencionar que las labores se ejecutaron bajo la mentoría y supervisión de Arquitectos y Líderes de Soluciones Senior.
- ❌ **ESTRICTAMENTE PROHIBIDO**:
  - Emplear títulos senior o de planta ("Senior Data Engineer", "Cloud Architect", "Staff Engineer", "Principal Lead").
  - Afirmar continuidad laboral o empleo formal en GBM más allá del 15 de octubre de 2026.
  - Afirmar que fue el responsable único de la entrega en producción ante clientes finales sin supervisión corporativa.
  - Declarar que las cartas `.docx` están legalmente firmadas mientras contengan placeholders pendientes de firma digital.

---

### 2.3 Proyecto Insignia: FERROSTATS (Medallion Lakehouse en GCP)

#### Contexto y Artefactos Primarios
- **Artefactos Primarios**: Repositorios de código fuente en `github.com/bapatata688/Ferrostats` y `github.com/b0ldm6diego`.
- **Naturaleza del Proyecto**: **Proyecto de portafolio personal de ingeniería de datos y analítica empresarial**. Desarrollado para demostrar capacidades avanzadas en arquitectura cloud, orquestación analítica y optimización de costos.

#### Especificación de Arquitectura y Rendimiento
- **Arquitectura Medallion en Google Cloud Platform**:
  - *Capa Bronze*: Ingesta asíncrona de 4 tablas crudas hacia BigQuery mediante APIs REST desacopladas con latencia en el borde inferior a **50 ms** (<50 ms), complementada por base de datos POS local en SQLite con transacciones ACID completas y modo WAL.
  - *Capa Silver*: 3 vistas staging en Google Dataform (SQLX) con aserciones automatizadas de calidad de datos (unicidad de claves primarias, validación de integridad referencial y restricciones de no-nulidad).
  - *Capa Gold*: 3 data marts analíticos estructurados bajo modelado Kimball Star Schema (`fct_daily_sales`, `mart_inventory_pareto_abc`, `dim_products`).
- **Analítica de Negocio y BI**: Lógica de inventarios basada en segmentación Pareto ABC (80/20) implementada con Window Functions de SQL, cálculo de Tasa de Consumo Diario (*Daily Burn Rate*) y Días de Inventario (*Days of Inventory - DOI*) con buffer de seguridad de 15 días, consumidos por un dashboard ejecutivo de 3 páginas en Looker Studio.
- **FinOps y Eficiencia de Costos**: Costo operativo mensual garantizado de **$0.00 USD/mes en GCP**, logrado mediante el aprovechamiento de Cloud Run con escalado a cero (cold start <3s), autenticación *keyless* con Service Accounts y poda automatizada de imágenes en Artifact Registry (<0.3 GB).

#### Límites de Contención Ética
- ✅ **PERMITIDO**:
  - Describir FERROSTATS como un proyecto de portafolio de ingeniería de datos cloud-native y POS Lakehouse.
  - Detallar el flujo Medallion Bronze/Silver/Gold en BigQuery + Dataform SQLX.
  - Citar la latencia de borde (<50 ms) y la arquitectura FinOps de $0.00/mes.
- ❌ **ESTRICTAMENTE PROHIBIDO**:
  - Presentar a FERROSTATS como una empresa comercial constituida, startup en operaciones o producto SaaS con clientes de pago o métricas de ingresos recurrentes ($MRR, ARR).
  - Afirmar que cuenta con clústeres distribuidos de PySpark operando de forma continua en producción (el procesamiento distribuido con PySpark es parte de la hoja de ruta de estudio y benchmark).
  - Exagerar volúmenes transaccionales por encima de las pruebas sintéticas de estrés documentadas (~15,000 peticiones/mes).

---

### 2.4 Plataforma de Entrenamiento: SQL Arena

#### Contexto y Artefactos Primarios
- **Artefactos Primarios**: Directorio de la plataforma en `c:\Users\Usuario\Projects\sql-arena` y `c:\Users\Usuario\Projects\coe\apps\sql-arena`.
- **Naturaleza del Proyecto**: **Plataforma web interactiva local de entrenamiento técnico en SQL** estilo LeetCode y HackerRank para preparación de entrevistas de Data Engineering.

#### Especificación de Software e Ingeniería de Aislamiento
- **Stack Tecnológico**: Frontend moderno en React 19 + Vite + Tailwind CSS v4 + Monaco Editor; Backend en Node.js + Express + MySQL 8.0 Community Server.
- **Mecanismos de Resiliencia y Aislamiento de Sandbox**:
  - `ExecutionMutex`: Mutex en memoria que serializa las transacciones asíncronas de reinicio de esquemas para evitar la contención de bloqueos de archivos InnoDB (`.ibd`) característica de Windows NTFS.
  - Parser léxico AST: Analizador sintáctico que inspecciona y bloquea inyecciones SQL mediante comentarios y sentencias múltiples (*multi-statements*).
  - Inspección de paquetes crudos `fields`: Extracción de metadatos del driver binario de MySQL preservando el esquema tipado de columnas incluso ante resultados vacíos (0 filas).
  - Timeout estricto de ejecución: Límite duro de 5,000 ms (`SET SESSION max_execution_time = 5000`).
- **Currículum y Suite de Calidad**: 34 problemas técnicos diseñados en 11 módulos temáticos; suite de pruebas automatizadas con **136 tests pasando al 100% de efectividad**.

#### Distinción Crítica e Innegociable: Creador vs Usuario
- **Como Autor y Arquitecto del Sistema**: Diego diseñó e implementó el 100% del software, el motor de ejecución aislado, la suite de 136 tests de regresión y el currículum de 34 problemas.
- **Como Usuario / Estudiante**: Diego ha resuelto y verificado en telemetría de usuario **3 de los 34 ejercicios** (`nulls-1`, `nulls-2`, `nulls-3`), encontrándose en curso de resolver `rounding-1`.

#### Límites de Contención Ética
- ✅ **PERMITIDO**:
  - Declararse "Creador y Arquitecto Full-Stack de SQL Arena".
  - Describir la autoría de la suite de 136 tests automatizados y el currículum de 34 desafíos de ingeniería.
  - Indicar con total honestidad el progreso de resolución como candidato (3 de 34 resueltos).
- ❌ **ESTRICTAMENTE PROHIBIDO**:
  - Afirmar que el candidato ha completado o resuelto los 34 ejercicios de la plataforma como usuario.
  - Describir a SQL Arena como una plataforma SaaS multi-inquilino en la nube con miles de usuarios activos.

---

### 2.5 Formación Académica, Certificaciones Oficiales e Idiomas

#### University of the People (UoPeople)
- **Estado Académico**: **Admitido formalmente** para iniciar en **Term 3, 2027 (28 de enero de 2027)**. Acuerdo *Save Your Spot* firmado el 06 de noviembre de 2026.
- **Carrera**: Bachelor of Science in Computer Science.
- **Institución**: University of the People, Pasadena, California, USA.
- **Acreditación**: Institución acreditada por WSCUC (WASC Senior College and University Commission). Modalidad 100% en Línea.
- **Bloque Mandatorio Verbatim (Cumplimiento de Contrato)**:
  - *Inglés*:
    > **University of the People** — Pasadena, California, USA  
    > **Bachelor of Science in Computer Science**  
    > Admitted | Term 3, 2027  
    > WSCUC-accredited institution | 100% Online
  - *Español*:
    > **University of the People** — Pasadena, California, EE. UU.  
    > **Bachelor of Science in Computer Science**  
    > Admitido | Term 3, 2027  
    > Institución acreditada por WSCUC | 100% en Línea

#### Instituto Nacional San Luis (INSAL)
- **Título**: Bachillerato Técnico Vocacional en Desarrollo de Software (NIE: 5450732, Código de Infraestructura: 11708).
- **Rendimiento Académico**: Promedio acumulado oficial de **9.5 / 10.0** (GPA ~3.8-4.0).
- **Cronograma Formal**: Culminación de clases presenciales: 30 de octubre de 2026. Graduación oficial: 10 de diciembre de 2026. Entrega formal del título registrado por MINEDUCYT con sellos en tinta húmeda: **Primer trimestre de 2027**.

#### Certificaciones Oficiales Verificadas
1. **Google Cloud Certified — Associate Data Practitioner**:
   - Certificado ID: `23e3584a246f4c149f26fea03cebcbbb`.
   - Fecha de Emisión: 23 de octubre de 2026. Vencimiento: 23 de octubre de 2029.
   - Entidad Emisora: Google Cloud | Verificación oficial vía Pearson VUE y Credly Badge `e27fea72-5eaf-47ee-a43c-43faa3a8fb10`.
2. **EF SET Certificate (English Proficiency)**:
   - Certificado Oficial: `https://cert.efset.org/93nXaa` (Emitido el 10 de enero de 2026).
   - Puntaje Global Oficial: **66/100 (C1 Advanced)**.
   - Desglose por Habilidad:
     - **Listening**: **75/100 (C2 Proficient)** *(Destreza destacada)*.
     - **Speaking**: **69/100 (C1 Advanced)**.
     - **Reading**: **67/100 (C1 Advanced)**.
     - **Writing**: **51/100 (B2 Upper Intermediate)**.
   - **Regla de Neutralización Crítica de Discrepancia**: Queda formalmente prohibida cualquier mención a "EF SET 95/100". Este valor fue un error tipográfico no comprobado en borradores preliminares de cartas; el único puntaje legal y verificable es 66/100 C1.

#### Límites de Contención Ética
- ✅ **PERMITIDO**:
  - Declarar la admisión formal a UoPeople para Term 3, 2027.
  - Citar el promedio 9.5/10.0 de INSAL y la entrega de título en Q1 2027.
  - Declarar la certificación Google Cloud Associate Data Practitioner con su ID oficial.
  - Declarar la certificación EF SET C1 Advanced (66/100) con nivel C2 en Listening (75/100).
- ❌ **ESTRICTAMENTE PROHIBIDO**:
  - Afirmar que ya ha completado materias o que está graduado de University of the People.
  - Reclamar la certificación Google Cloud Professional Data Engineer (PDE) antes de aprobar su examen formal.
  - Reclamar "EF SET 95/100" (constituye falta grave de veracidad).

---

## 3. TABLA CONSOLIDADA DE CONTENCIÓN (VERIFICABLE VS PROHIBIDO)

| Dominio Técnico | Hecho Verificable (Inclusión Aprobada) | Límites Estrictos de Contención | Expresiones Estrictamente Prohibidas (Linter FATAL) | Artefacto Primario de Verificación |
|:---|:---|:---|:---|:---|
| **Investigación OntoTab** | Coautor (2.º de 7), líder de Actividad E01 (baselines R0 y R8 sobre 30k registros, 5x3 CV, 2,000 bootstraps, 0.5596 AP XGBoost). | Manuscrito de investigación interna en GBM. Autorizado para adjuntar en postulaciones. | `Machine Learning Engineer`, `Lead Author`, `Principal Investigator`, `IEEE`, `ACM`, `NeurIPS`, `peer-reviewed`. | `research/ontotab/OntoTab-finaledit.pdf` |
| **Experiencia GBM** | Digital Solutions Specialist Intern (Data & AI), 13 semanas (julio a octubre 2026), 15 jobs DataStage, DB2 LUW, propuesta ELT GCP, CLI Python SDD. | Cargo de pasantía bajo supervisión técnica senior. Finiquito el 15 de octubre de 2026. | `Senior Data Engineer`, `Cloud Architect`, `Staff Engineer`, `Lead Data Engineer`, empleo más allá de oct/2026. | `recommendations/en/Recommendation_Letter_Diego_Escobar_EN.docx`, LinkedIn. |
| **Proyecto FERROSTATS** | Lakehouse Medallion personal en GCP (BigQuery + Dataform SQLX), POS SQLite ACID, latencia <50ms, costo $0.00/mes FinOps. | Proyecto de portafolio personal y demostración técnica. Sin ingresos comerciales. | `startup`, `paying clients`, `revenue-generating`, `$MRR`, `production PySpark cluster`. | `github.com/bapatata688/Ferrostats` |
| **Proyecto SQL Arena** | Creador y Arquitecto Full-Stack (React 19, Monaco, Express, MySQL 8), 136 tests pasando, 34 problemas en currículo. | Distinción autor vs estudiante. Progreso como estudiante en telemetría: 3/34 resueltos. | `completed all 34 exercises`, `solved 34/34`, `commercial SaaS`, `thousands of active users`. | `c:/Users/Usuario/Projects/sql-arena/README.md`, `sql_progress.txt`. |
| **Inglés EF SET** | Certificación EF SET C1 Advanced, puntaje global 66/100, Listening 75/100 (C2 Proficient). | Verificación pública activa en cert.efset.org/93nXaa. | `95/100`, `EF SET 95`, `95% EF SET`. | `certifications/EF_SET_Certificate_C1_Advanced.pdf` |
| **Certificación Cloud** | Google Cloud Certified Associate Data Practitioner, Cert ID `23e3584a246f4c149f26fea03cebcbbb`, Pearson VUE. | Credencial a nivel de practicante asociado vigente hasta octubre de 2029. | `Professional Data Engineer`, `GCP PDE`. | `certifications/Google_Cloud_Certified_Associate_Data_Practitioner.pdf` |
| **Educación Superior** | University of the People: Admitido para Term 3, 2027 (enero 2027), B.S. in Computer Science. | Admisión formal documentada; carrera no iniciada aún. | `graduated from University of the People`, `B.S. degree awarded`. | `perfil_integral_maestro.md`, Carta de Admisión. |
| **Educación Media** | INSAL: Bachillerato Técnico en Desarrollo de Software, GPA 9.5/10.0, título MINEDUCYT en Q1 2027. | Graduación en diciembre 2026, entrega de título físico en Q1 2027. | Título en mano antes de 2027. | `ORIGINAL_REQUEST.md`, Boletas SIGES 2024-2025. |

---

## 4. CONTRATO DE INTEGRACIÓN CON EL LINTER ÉTICO (MILESTONE 4)

El archivo `master_cv/resources/evidence_matrix.json` sirve como contrato técnico directo para el ejecutable de auditoría estática `scripts/lint_cv_truth.py` desarrollado en Milestone 4.

### 4.1 Mecanismo de Validación en el Pipeline CI/CD
El linter ejecuta una inspección en tres fases consecutivas sobre todos los archivos de plantillas HTML y documentación:
1. **Fase 1: Escaneo de Expresiones Regulares Prohibidas (*Forbidden Regex Scan*)**:
   Compila la lista negra global y por dominio (`GLOBAL-FORBID-*`, `FORBID-ONTO-*`, `FORBID-GBM-*`, `FORBID-FERRO-*`, `FORBID-SQLA-*`, `FORBID-EF-*`, `FORBID-EDU-*`). Si algún patrón encuentra una coincidencia en el texto, el linter imprime el número de línea, la regla violada y el motivo forense, abortando inmediatamente la ejecución con código de salida `1` (`exit code 1`).
2. **Fase 2: Verificación de Declaraciones Obligatorias (*Required Disclosure Check*)**:
   Valida que los bloques mandatorios (tales como la posición de autoría "2nd of 7" en OntoTab o el formato contractual verbatim de University of the People) estén presentes de manera íntegra.
3. **Fase 3: Verificación de Tolerancia Métrica (*Metric Bounds Check*)**:
   Extrae y analiza los valores numéricos citados en el texto (volumen de registros = 30,000, jobs DataStage = 15, semanas GBM = 13, costo FERROSTATS = $0.00, tests SQL Arena = 136). Si algún valor numérico excede los límites definidos, la compilación WeasyPrint de PDFs es cancelada.

---

## 5. GUÍA DE DEFENSA EN ENTREVISTAS TÉCNICAS (PREVIEW MILESTONE 3)

El arnés de contención no es una limitación, sino la base de la solidez profesional de Diego Escobar en entrevistas técnicas ante reclutadores e ingenieros de personal senior. A continuación se presentan las directrices de defensa táctica que Milestone 3 expandirá en el `INTERVIEW_DEFENSE_MANUAL.md`:

### Caso 1: Preguntas sobre OntoTab y Autoría
- **Pregunta del Entrevistador**: *"Veo que tienes un paper de investigación sobre OntoTab con 30,000 registros crediticios. ¿Cuál fue exactamente tu contribución y por qué el modelo textual no superó al numérico?"*
- **Estrategia Defensiva**: Explicar con total naturalidad que el proyecto fue desarrollado en GBM bajo el liderazgo de Joaquín Solórzano, donde Diego asumió como segundo autor el liderazgo de la Actividad Experimental E01 (los baselines numéricos puros). Defender que la preservación de canales numéricos estructurados (0.5596 AP en XGBoost) superó a la verbalización ontológica (0.5069 AP), lo que demuestra un criterio de ingeniería pragmático: *"No añadir complejidad de NLP a datos tabulares si las variables numéricas limpias ofrecen mayor poder predictivo"*.

### Caso 2: Preguntas sobre SQL Arena y Progreso de Resolución
- **Pregunta del Entrevistador**: *"¿Has completado todos los ejercicios de tu plataforma SQL Arena?"*
- **Estrategia Defensiva**: Aclarar de inmediato la distinción de roles: *"Como arquitecto de la plataforma, diseñé los 34 desafíos técnicos y escribí la suite de 136 tests automatizados en Node.js y MySQL para evaluar casos de borde como nulos en 3VL y colisiones de bloqueos NTFS. Como usuario que resuelve los retos en el sandbox interactivo, he completado formalmente 3 de los 34 ejercicios iniciales y sigo avanzando en el plan de estudio diario"*. Esta respuesta proyecta madurez, honestidad y maestría de arquitectura de software.

### Caso 3: Preguntas sobre FERROSTATS y FinOps
- **Pregunta del Entrevistador**: *"¿FERROSTATS tiene clientes reales de pago o es un proyecto de demostración?"*
- **Estrategia Defensiva**: *"Es un proyecto de portafolio de ingeniería de datos cloud-native diseñado bajo restricciones reales de producción. Mi objetivo fue implementar un Lakehouse Medallion completo (Bronze/Silver/Gold) en BigQuery con aserciones automáticas en Dataform, garantizando al mismo tiempo un costo de infraestructura permanente de $0.00/mes mediante Cloud Run con escala a cero y poda de artefactos"*. Demuestra conciencia de negocio y disciplina FinOps.

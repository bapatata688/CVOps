# BANCO DE PREGUNTAS TÉCNICAS Y CONDUCTUALES (QUESTION BANK)

Este documento compila el banco exhaustivo de preguntas de entrevista estructuradas por persona evaluadora y proyecto objetivo para la preparación de Diego Escobar.

---

## 1. PREGUNTAS TÉCNICAS (TECH LEAD & ARCHITECT)

### T-01: Arquitectura Medallion en FERROSTATS
- **Pregunta**: "¿Cómo implementaste el flujo Medallion Bronze -> Silver -> Gold en Google Cloud y por qué elegiste SQLite con WAL en el borde?"
- **Objetivo**: Evaluar la comprensión del desacoplamiento OLTP vs OLAP, latencia en el borde (<50 ms), transacciones ACID locales y modelado Kimball en BigQuery con Dataform SQLX.
- **Puntos Clave**: Ingesta REST asíncrona, aserciones automatizadas de unicidad y no-nulidad en Silver, 3 data marts Gold (`fct_daily_sales`, `mart_inventory_pareto_abc`, `dim_products`), y arquitectura FinOps de $0.00/mes con Cloud Run scale-to-zero.

### T-02: Concurrencia y Aislamiento en SQL Arena
- **Pregunta**: "Explica el problema de concurrencia en Windows NTFS que resolviste con el `ExecutionMutex` y cómo proteges el sandbox de MySQL 8 contra inyecciones."
- **Objetivo**: Evaluar conocimientos profundos de sistemas operativos, contención de bloqueos en archivos InnoDB (`.ibd`), parser léxico AST de sentencias únicas e inspección de paquetes crudos `fields` del driver binario.
- **Puntos Clave**: Mutex asíncrono en memoria, timeout estricto de 5,000 ms, suite de 136 tests automatizados y reporte transparente del avance como estudiante (3/34 resueltos).

### T-03: Integración ETL en IBM DataStage y DB2
- **Pregunta**: "¿Cuáles fueron los desafíos técnicos más relevantes al construir los 15 jobs en IBM InfoSphere DataStage y administrar DB2 LUW sobre Linux RHEL en GBM?"
- **Objetivo**: Evaluar manejo de herramientas empresariales de integración, stages de DataStage (Transformers, Lookups, Joins, Merge, Funnel), tratamiento de nulos y consultas sobre Red Hat Enterprise Linux.

---

## 2. PREGUNTAS DE INVESTIGACIÓN Y MACHINE LEARNING (ML RESEARCHER)

### ML-01: OntoTab y la Superioridad del Baseline Numérico
- **Pregunta**: "En OntoTab, ¿por qué el baseline numérico R8 en XGBoost (0.5596 AP) superó a la representación de texto ontológico denso R5 (0.5069 AP)?"
- **Objetivo**: Evaluar el diseño experimental de la Actividad E01 liderada por Diego, el uso de 30,000 registros de UCI Taiwán, validación anidada 5×3 y 2,000 bootstraps pareados.
- **Puntos Clave**: Dilución de límites numéricos continuos en embeddings densos de 1,024 dimensiones de BGE-M3 congelado; capacidad superior de XGBoost para particionar el espacio tabular continuo; resultado estadísticamente significativo respaldado por el autor principal Joaquín Solórzano.

### ML-02: Desbalance de Clases y Selección de Métricas
- **Pregunta**: "¿Por qué se eligió Average Precision (PR-AUC) en lugar de ROC-AUC para evaluar el modelo de predicción de incumplimiento crediticio?"
- **Objetivo**: Evaluar rigor estadístico frente al desbalance de clases (22.12% de mora) y la distorsión que generan los verdaderos negativos en ROC-AUC.

---

## 3. PREGUNTAS CONDUCTUALES Y DE AJUSTE (RECRUITER & HIRING MANAGER)

### B-01: Trayectoria, Pasantía en GBM y Transición Profesional
- **Pregunta**: "Háblame de tu transición del bachillerato técnico en desarrollo de software hacia la ingeniería de datos y tu pasantía de 13 semanas en GBM."
- **Objetivo**: Evaluar motivación intrínseca, madurez profesional, consistencia en fechas y claridad comunicativa.

### B-02: Educación Superior y Dominio del Idioma Inglés
- **Pregunta**: "¿Cómo compaginas tus metas laborales con tus estudios universitarios y cuál es tu nivel certificado de inglés?"
- **Objetivo**: Evaluar la admisión formal para Term 3, 2027 en University of the People (B.S. in CS, 100% online, Pasadena, CA) y el certificado oficial EF SET C1 Advanced (66/100, Listening 75 C2).

---

## 4. PREGUNTAS DE AUDITORÍA FORENSE (AUDITOR & SCREENER)

### A-01: Disolución de la Errata Tipográfica EF SET 95/100 vs 66/100
- **Pregunta**: "Detectamos una mención preliminar a un puntaje de 95/100 en cartas preliminares. ¿Cuál es el estatus oficial de tu certificación de inglés?"
- **Objetivo**: Probar la honestidad inquebrantable del candidato. Se responde confirmando que 95/100 fue una errata de borrador eliminada de raíz, y se ratifica el certificado oficial de 66/100 C1 Advanced (Listening 75 C2) emitido por EF SET el 10/Ene/2026.

### A-02: Delimitación de Autoría en OntoTab
- **Pregunta**: "¿Fuiste el autor principal o único de la investigación OntoTab?"
- **Objetivo**: Verificar que el candidato no asuma títulos indebidos. Diego declara con orgullo que es el 2.º autor de 7 autores, líder de la Actividad Experimental E01 de baselines, bajo la dirección del primer autor Joaquín Solórzano.

# CATÁLOGO DE ANTIPATRONES Y LÍMITES ÉTICOS (ANTI-PATTERNS)

Este documento cataloga las trampas verbales recurrentes, malas prácticas y afirmaciones estrictamente prohibidas durante los procesos de entrevista de Diego Escobar.

---

## 1. ANTIPATRONES DE INFLACIÓN DE TÍTULOS (SENIORITY INFLATION)

### Antipatrón 1.1: Inflar el Cargo de Pasantía en GBM
- **Formulación Prohibida**: *"Me desempeñé como Senior Data Engineer o Ingeniero de Machine Learning en GBM liderando el área de datos."*
- **Por qué Falla**: Diego tuvo un rol formal de pasante ("Digital Solutions Specialist Intern") durante 13 semanas bajo la supervisión de un Product Owner y un AI Team Lead. Reclamar un título senior destruye la credibilidad técnica ante verificadores de antecedentes.
- **Formulación Correcta**: *"Durante mi pasantía de 13 semanas como Digital Solutions Specialist Intern en GBM, co-diseñé una propuesta de arquitectura ELT en GCP, construí 15 jobs en IBM DataStage y administré DB2 en RHEL."*

### Antipatrón 1.2: Asumir Autoría Principal en OntoTab
- **Formulación Prohibida**: *"Fui el autor líder de la investigación OntoTab y publiqué el descubrimiento en IEEE."*
- **Por qué Falla**: El autor líder e investigador principal es Joaquín Francisco Solórzano Corea. Diego es formalmente el 2.º autor de 7, a cargo de la Actividad Experimental E01 de baselines. El artículo es un manuscrito de investigación interna en GBM, no una publicación indexada en IEEE.
- **Formulación Correcta**: *"Fui coautor (segundo autor de 7) de la investigación OntoTab en GBM, liderando la Actividad Experimental E01 donde evalué baselines numéricos sobre 30,000 registros logrando 0.5596 AP en XGBoost."*

---

## 2. ANTIPATRONES DE MÉTRICAS Y PROGRESO (METRIC EXAGGERATION)

### Antipatrón 2.1: Defender el Typo Histórico de Inglés 95/100
- **Formulación Prohibida**: *"Tengo 95/100 en el examen de inglés de EF SET."*
- **Por qué Falla**: Es un dato falso originado en una errata de borrador. El certificado oficial y verificable en Pearson / EF SET acredita **66/100 (C1 Advanced)** con **75/100 en Listening (C2 Proficient)**. Defender 95/100 activa una bandera roja por falsificación de credenciales.
- **Formulación Correcta**: *"Cuento con certificación EF SET C1 Advanced con 66/100 en puntaje general y 75/100 en Listening, lo que equivale a nivel C2 Proficient."*

### Antipatrón 2.2: Afirmar haber resuelto los 34 problemas de SQL Arena
- **Formulación Prohibida**: *"He resuelto y completado todos los 34 problemas de SQL Arena."*
- **Por qué Falla**: Confunde el rol de Arquitecto del sistema con el progreso de usuario. La telemetría de usuario registra 3 problemas completados (`nulls-1`, `nulls-2`, `nulls-3`).
- **Formulación Correcta**: *"Diseñé y programé el 100% de la plataforma SQL Arena, incluyendo el sandbox en MySQL 8, los 136 tests de regresión y los 34 desafíos de arquitectura; como estudiante usuario he resuelto 3 de los 34 problemas hasta la fecha."*

---

## 3. ANTIPATRONES DE COMERCIALIZACIÓN FICTICIA (FAUX COMMERCIALIZATION)

### Antipatrón 3.1: Presentar Proyectos de Portafolio como Startups con Ingresos
- **Formulación Prohibida**: *"FERROSTATS es una startup comercial que genera ingresos mensuales recurrentes con múltiples clientes corporativos."*
- **Por qué Falla**: FERROSTATS es un proyecto de portafolio de ingeniería de datos y arquitectura cloud-native diseñado para demostrar habilidades técnicas de vanguardia y FinOps ($0.00/mes).
- **Formulación Correcta**: *"FERROSTATS es un proyecto de portafolio personal en Google Cloud Platform donde demostré arquitectura Medallion, streaming desacoplado POS con latencia en el borde <50 ms y optimización FinOps para operar a costo cero."*

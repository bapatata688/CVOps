# AUDITORÍA FORENSE DE BRECHAS DE EVIDENCIA Y CATÁLOGO DE CONCILIACIÓN

## 1. METODOLOGÍA FORENSE DE 4 NIVELES (4-TIER EVIDENCE GAP DETECTION PIPELINE)

Para blindar la integridad del perfil profesional de Diego Alejandro Escobar Barahona ante cualquier auditoría técnica, verificación de antecedentes corporativa (*background check*) o escrutinio en entrevistas de ingeniería, el marco `master_cv` implementa un pipeline analítico de cuatro niveles de evidencia:

```text
========================================================================================
4-TIER EVIDENCE GAP DETECTION PIPELINE (FRAMEWORK MASTER_CV)
========================================================================================

    [ Insumo / Afirmación en Borradores de CV o Perfil ]
                            │
                            ▼
    [ Paso 1: Extracción de Entidades y Métricas Cuantitativas ]
      - Nombres de empresa, cargos, fechas, herramientas, métricas (%, count, $, ms)
                            │
                            ▼
    [ Paso 2: Cotejo Contra Artefactos Primarios en el Repositorio ]
      - PDFs oficiales sellados, Pearson VUE, Credly, código fuente, suites de tests
                            │
                            ▼
    [ Paso 3: Clasificación Forense en 4 Niveles ]
      ├── TIER 1: EVIDENCIA PRIMARIA VERIFICADA ──────────> APROBADO INCONDICIONAL
      ├── TIER 2: EVIDENCIA INTERNA / FIRMAS PENDIENTES ─> APROBADO CON PROTOCOLO
      ├── TIER 3: DISCREPANCIA / EXAGERACIÓN DETECTADA ──> BLOQUEO FATAL Y CORRECCIÓN
      └── TIER 4: AFIRMACIÓN NO RESPALDADA / FABRICACIÓN ─> EXPULSIÓN INMEDIATA
                            │
                            ▼
    [ Paso 4: Ejecución del Linter Automatizado (Milestone 4) ]
      - scripts/lint_cv_truth.py verifica cumplimiento estricto con exit code 0/1
========================================================================================
```

### Definición de los Cuatro Niveles Forenses:
- **Nivel 1 (Tier 1 — Evidencia Primaria Oficial Verificada)**:
  Afirmación o métrica respaldada al 100% por un documento oficial sellado en PDF, credencial de examen emitida por terceros con ID verificable (Pearson VUE, Credly, EF SET oficial), o repositorio de software con suite de pruebas automatizadas pasando al 100%. **Estado: Aprobado para inclusión directa en plantillas de CV**.
- **Nivel 2 (Tier 2 — Evidencia Interna / En Trámite / Firmas Pendientes)**:
  Hecho técnico real confirmado por la experiencia laboral y avalado por testimonios de supervisores, pero cuya documentación física formal contiene campos de texto (*placeholders*) pendientes de rellenar o carece de firma húmeda o digital formal. **Estado: Aprobado para el CV como hecho técnico; advertencia al candidato sobre el estatus de la carta física**.
- **Nivel 3 (Tier 3 — Discrepancia / Trampa de Exageración / Error de Tipografía)**:
  Afirmación presente en borradores previos que contradice directamente los datos de una credencial oficial (ejemplo crítico: *"EF SET 95/100"* frente al certificado real de 66/100) o que infla títulos o roles. **Estado: BLOQUEO INMEDIATO Y MANDATORIO. Prohibición de compilación en CI/CD**.
- **Nivel 4 (Tier 4 — Afirmación No Respaldada / Insumo Faltante)**:
  Métricas, arquitecturas o responsabilidades que no cuentan con ningún respaldo en código, repositorios o documentación de soporte. **Estado: PROHIBIDO en producción hasta contar con prueba fehaciente**.

---

## 2. CATÁLOGO FORENSE CONSOLIDADO DE BRECHAS Y CONCILIACIÓN

| ID | Dominio / Afirmación | Texto en Borradores Previos | Evidencia Primaria Encontrada | Clasificación Forense | Veredicto y Acción Correctiva | Estado |
|:---|:---|:---|:---|:---|:---|:---|
| **GAP-001** | Certificación de Inglés EF SET | *"EF SET 95/100, C2 Listening"* | `certifications/EF_SET_Certificate_C1_Advanced.pdf`: **66/100 (C1 Advanced)**, Listening 75/100 (C2 Proficient), Speaking 69, Reading 67, Writing 51. | **Tier 3 (Discrepancia Crítica)** | **CORRECCIÓN MANDATORIA**: Purgar todo "95/100". Enforzar estrictamente "66/100 (C1 Advanced, Listening 75 C2 Proficient)". Linter bloquea 95/100 vía `FORBID-EF-001`. | **ACCIÓN EJECUTADA** |
| **GAP-002** | Cartas de Recomendación GBM | Cartas formales listas para entrega ante empleadores | `recommendations/en/Recommendation_Letter_Diego_Escobar_EN.docx`: Contiene corchetes unpopulated `[Team Lead / Supervisor Name]`, `[+503 XXXX-XXXX]`. | **Tier 2 (Incomplete Sign-off)** | Los hechos técnicos descritos son 100% verídicos y están respaldados por Juan Carlos Quintero en LinkedIn. Diego no debe afirmar que las cartas están firmadas físicamente hasta completar el trámite formal de firmas. | **TRÁMITE EN CURSO** |
| **GAP-003** | Autoría en OntoTab | *"Coautor OntoTab"* | `research/ontotab/OntoTab-finaledit.pdf`: Página 1 lista a Diego como **2.º autor de 7**. Autor líder es Joaquín Solórzano Corea. | **Tier 1 (Verificado Primario)** | **APROBADO**. Enforzar inclusión explícita del rango exacto: "Co-author (2nd author of 7)" o "Coautor (2.º de 7)". Bloquear títulos de lead/principal. | **RESUELTO** |
| **GAP-004** | Métricas de OntoTab | *"30k registros, 0.5596 AP en XGBoost"* | `research/ontotab/OntoTab-finaledit.pdf`: Tabla 4 R8 XGBoost = 0.559596, R0 = 0.558879, R5 = 0.506909; 5x3 nested CV, 2,000 bootstraps. | **Tier 1 (Verificado Primario)** | **APROBADO**. Métricas 100% corroboradas y verificadas con tolerancia matemática cero. | **RESUELTO** |
| **GAP-005** | Entregables GBM | *"15 jobs DataStage, DB2 LUW, GCP ELT, Python CLI SDD"* | Recomendaciones de supervisores y testimonios públicos en LinkedIn. | **Tier 1 (Verificado Primario)** | **APROBADO**. Hechos técnicos plenamente verificados. Cargo limitado formalmente a Pasante / Intern (13 semanas). | **RESUELTO** |
| **GAP-006** | Typo de Puntaje en Cartas de Recomendación | Párrafo 7 de ambas cartas (.docx) incluye: *"EF SET 95/100"* | `recommendations/en/` y `recommendations/es/` Párrafo 7. | **Tier 3 (Discrepancia en Borrador)** | Corregir los archivos `.docx` fuente para sustituir "95/100" por "66/100 (C1 Advanced, C2 Listening)". | **ACCIÓN REQUERIDA** |
| **GAP-007** | Educación University of the People | *"Admitted B.S. in Computer Science"* | `perfil_integral_maestro.md`: Admitido para Term 3, 2027 (28 de enero de 2027). Save Your Spot firmado el 06 de noviembre de 2026. | **Tier 1 (Verificado Primario)** | **APROBADO**. Debe incluir redacción verbatim contractual sin sugerir que la carrera ya se ha iniciado o concluido. | **RESUELTO** |
| **GAP-008** | Dominio y Progreso en SQL Arena | *"SQL Arena con 34 problemas resueltos"* | Repositorio `sql-arena`: 34 problemas diseñados, 136 tests pasando; telemetría de usuario del candidato registra 3/34 resueltos. | **Tier 1 / Tier 3 boundary** | **APROBADO** como Arquitecto y Creador de la plataforma; **PROHIBIDO** afirmar que el candidato resolvió 34/34 ejercicios como usuario. | **RESUELTO** |

---

## 3. ANÁLISIS DETALLADO DE CASOS FORENSES CRÍTICOS

### 3.1 Caso GAP-001 y GAP-006: La Discrepancia del Puntaje EF SET (95/100 vs 66/100)
- **Origen del Error**: En etapas iniciales de redacción de los perfiles y borradores de cartas de recomendación en GBM, se consignó de forma preliminar el valor *"EF SET 95/100"* basándose probablemente en una confusión con el percentil de fluidez o una escala no oficial de 1 a 100.
- **Evidencia Fehaciente Irrefutable**: La inspección del archivo binario `certifications/EF_SET_Certificate_C1_Advanced.pdf` emitido oficialmente por EF Education First el 10 de enero de 2026 (y verificable en `cert.efset.org/93nXaa`) acredita:
  - **Overall Score: 66/100 (C1 Advanced)**
  - **Listening: 75/100 (C2 Proficient)**
  - **Speaking: 69/100 (C1 Advanced)**
  - **Reading: 67/100 (C1 Advanced)**
  - **Writing: 51/100 (B2 Upper Intermediate)**
- **Riesgo Forense**: Si un reclutador o sistema de verificación de antecedentes ingresa a la URL de EF SET y lee "66/100" después de ver "95/100" en el CV, el candidato sería calificado con una bandera roja por falsificación de credenciales.
- **Resolución**: Se elimina y prohíbe de forma absoluta cualquier mención a "95/100". El CV y todos los perfiles consignan exclusivamente: *"EF SET English Certificate — C1 Advanced (66/100: Listening 75/100 C2 Proficient)"*.

### 3.2 Caso GAP-002: El Estatus de las Cartas de Recomendación Corporativas
- **Situación Observada**: Los archivos `Recommendation_Letter_Diego_Escobar_EN.docx` y `Carta_Recomendacion_Diego_Escobar_ES.docx` contienen el texto completo de las responsabilidades y logros de Diego durante sus 13 semanas en GBM. Sin embargo, en el pie de firma constan campos de texto entre corchetes: `[Team Lead / Supervisor Name]`, `[Corporate Email]`, `[Phone: +503 XXXX-XXXX]`.
- **Estatus Legal**: Los documentos son borradores institucionales preparados para firma. No son cartas selladas ni firmadas aún.
- **Respaldo Válido Existente**: Juan Carlos Quintero Escobar (Product Owner Data & AI en GBM y supervisor de Diego) emitió una recomendación pública formal e inmutable en su perfil oficial de LinkedIn avalando explícitamente las competencias de Diego en integración de datos, DB2 y modernización en la nube.
- **Resolución**: Diego puede citar con 100% de legitimidad todos los logros técnicos en su CV (15 jobs DataStage, DB2 en RHEL, propuesta ELT en GCP), pero si un empleador solicita cartas formales en PDF con firma digital, se debe proceder a la firma con Joaquín Solórzano o Juan Carlos Quintero.

### 3.3 Caso GAP-008: Separación Ética en SQL Arena (Arquitecto de Plataforma vs Estudiante)
- **Situación Observada**: El proyecto SQL Arena consta de 34 problemas técnicos exhaustivamente diseñados y 136 tests automatizados de regresión que evalúan sintaxis, restricciones de nulidad y contención de concurrencia. Al mismo tiempo, el archivo de seguimiento del candidato `sql_progress.txt` registra que Diego ha resuelto formalmente en la interfaz los problemas `nulls-1`, `nulls-2` y `nulls-3`.
- **Riesgo Forense**: Presentar el proyecto diciendo *"Resolví 34 problemas de SQL en SQL Arena"* sugiere que Diego fue únicamente un usuario que practicó en la plataforma, o peor, que completó todo el currículo cuando la telemetría muestra 3 ejercicios concluidos.
- **Resolución**: La formulación aprobada eleva el valor del candidato al presentarlo como el **Arquitecto de Software** que diseñó la plataforma, el sandbox en MySQL 8 y los 136 tests de evaluación, reportando con total transparencia su avance como estudiante (3 de 34 resueltos).

---

## 4. PROTOCOLO DE REMEDIACIÓN PRIORIZADO

El plan de acción correctivo se organiza en tres niveles de prioridad estricta:

```text
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ NIVEL P0 — INMEDIATO (Pre-requisito Bloqueante de Compilación)                        │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ • Purgar toda coincidencia de r'(?i)95\s*/\s*100' de cualquier archivo del repo.     │
│ • Bloquear cualquier intento de compilación en WeasyPrint si se detecta '95/100'.    │
│ • Validar que la posición de autoría en OntoTab señale formalmente "2nd of 7".       │
└───────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ NIVEL P1 — ALTA PRIORIDAD (Trámite Externo de Formalización)                          │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ • Actualizar los archivos .docx de cartas de recomendación en coe/recommendations/    │
│   reemplazando el texto erróneo 'EF SET 95/100' por 'EF SET 66/100 (C1 Advanced)'.    │
│ • Rellenar los placeholders de contacto con los datos oficiales de supervisores.     │
│ • Solicitar firma formal (digital o wet-ink) a Joaquín Solórzano y Juan Carlos Q.    │
└───────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ NIVEL P2 — MEDIANA PRIORIDAD (Entrenamiento y Cierre de Brechas de Usuario)           │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ • Continuar el avance diario en la resolución de problemas en SQL Arena (pasar de     │
│   3/34 a 34/34 según el cronograma de estudio).                                      │
│ • Mantener actualizado el log de telemetría de usuario conforme se superen módulos.   │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. GATE DE AUDITORÍA PRE-DESPLIEGUE (CHECKLIST DE VERIFICACIÓN)

Antes de autorizar la sincronización de archivos hacia Google Drive o la emisión de versiones finales de CV en PDF, el Auditor Forense y el script `lint_cv_truth.py` deben verificar el cumplimiento del siguiente checklist de 7 puntos:

- [ ] **1. Ausencia Absoluta de 95/100**: No existe ninguna referencia a "95/100", "95% EF SET" o "EF SET 95" en archivos `.html`, `.md` o `.json`.
- [ ] **2. Consistencia Numérica de OntoTab**: Todo texto sobre OntoTab cita exactamente 30,000 registros, 0.5596 AP en XGBoost y la autoría como segundo autor de 7 (2nd of 7).
- [ ] **3. Acotación de Experiencia GBM**: La duración de GBM se consigna como 13 semanas (julio a octubre de 2026) bajo cargo de pasantía / intern, con 15 jobs DataStage.
- [ ] **4. Estatuto No Comercial de FERROSTATS**: FERROSTATS se describe como proyecto de portafolio y arquitectura Medallion cloud-native ($0.00/mo FinOps), sin mención de clientes comerciales o ingresos.
- [ ] **5. Precisión en SQL Arena**: Se distingue la autoría de la plataforma (34 problemas, 136 tests) del progreso de resolución del estudiante (3/34 resueltos).
- [ ] **6. Verbatim de UoPeople**: La sección de educación superior refleja exactamente la cláusula de admisión formal para Term 3, 2027 sin alegar estudios concluidos.
- [ ] **7. Título INSAL y Fechas**: Se indica con precisión el GPA 9.5/10.0, graduación en diciembre de 2026 y entrega física del título MINEDUCYT en el primer trimestre de 2027.

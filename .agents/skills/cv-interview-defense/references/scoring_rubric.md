# GUÍA DE CALIFICACIÓN Y RÚBRICAS STAR (SCORING RUBRIC)

Esta guía define los criterios analíticos de calificación sobre la escala de 1 a 5 puntos empleada por el evaluador automatizado `drill_runner.py` y los evaluadores humanos.

---

## 1. ESCALA GENERAL DE EVALUACIÓN (1 A 5 PUNTOS)

| Calificación | Descriptor | Criterios Técnicos y Estructurales |
|---|---|---|
| **5 / 5** | **Excelente / Defensa Verificada** | Cumple estrictamente la estructura STAR. Cita métricas cuantitativas exactas (0.5596 AP, 30,000 registros, 13 semanas, 15 jobs, <50 ms, $0.00/mes, 136 tests). Delimita con total transparencia los roles personales frente a la supervisión. Cero afirmaciones no respaldadas. |
| **4 / 5** | **Sólido / Competente** | Estructura STAR clara. Incluye la mayoría de las métricas clave con precisión técnica. Respeta los límites de autoría y roles sin inflar títulos. |
| **3 / 5** | **Aceptable con Observaciones** | Narrativa técnica comprensible pero con estructura STAR parcial. Alguna métrica se expresa de forma genérica o aproximada. Sin violaciones éticas. |
| **2 / 5** | **Deficiente** | Respuesta dispersa, sin métricas cuantitativas ni evidencia de ingeniería sólida. Vaguedad en el rol desempeñado. |
| **1 / 5** | **Inaceptable** | Desconocimiento de los aspectos técnicos fundamentales de sus propios proyectos. |
| **0 / 5** | **DESCALIFICACIÓN INMEDIATA (FAIL)** | **Penalización Fatal por Violación Ética**: Ocurre de forma automática si la respuesta contiene títulos inflados ("Senior Data Engineer", "Machine Learning Engineer"), falsedad en autoría ("Lead Author", "First Author"), sedes de publicación inexistentes ("Published in IEEE"), o calificaciones adulteradas ("95/100"). |

---

## 2. REGLAS AUTOMATIZADAS DE DEDUCCIÓN Y PENALIZACIÓN FATAL

El evaluador `drill_runner.py` aplica el siguiente protocolo determinista de deducciones:

```
[Respuesta del Candidato]
        │
        ├── ¿Contiene "Senior", "Staff" o "Lead Data Engineer"? ──────> [DEDUCCIÓN: -5 PTS] -> VEREDICTO: FAIL
        ├── ¿Contiene "Lead Author", "First Author" o "PI"? ──────────> [DEDUCCIÓN: -5 PTS] -> VEREDICTO: FAIL
        ├── ¿Contiene "Published in IEEE" o "Peer-reviewed"? ─────────> [DEDUCCIÓN: -5 PTS] -> VEREDICTO: FAIL
        ├── ¿Contiene "95/100" o "95% EF SET"? ───────────────────────> [DEDUCCIÓN: -5 PTS] -> VEREDICTO: FAIL
        ├── ¿Contiene "Solved all 34" o "34/34" en SQL Arena? ────────> [DEDUCCIÓN: -5 PTS] -> VEREDICTO: FAIL
        ├── ¿Contiene "Permanent role" o ">13 weeks" en GBM? ─────────> [DEDUCCIÓN: -5 PTS] -> VEREDICTO: FAIL
        │
        └── ¿Respuesta libre de violaciones y con anclas fácticas? ───> [ASIGNACIÓN: 5 PTS] -> VEREDICTO: PASS
```

---

## 3. CHECKLIST DE VERIFICACIÓN PARA EL EVALUADOR

- [ ] ¿Se enunciaron claramente la **Situación**, la **Tarea**, la **Acción** y el **Resultado**?
- [ ] ¿Se citaron las cifras oficiales sin redondeos excesivos?
- [ ] ¿Se especificó que en OntoTab Diego fue el **segundo autor** y líder del baseline E01?
- [ ] ¿Se confirmó que la pasantía en GBM duró exactamente **13 semanas** como pasante?
- [ ] ¿Se aclaró que en SQL Arena Diego es el creador de la plataforma (136 tests) y ha resuelto 3 ejercicios como usuario?
- [ ] ¿Se ratificó la calificación real de **66/100 C1 Advanced** en EF SET?

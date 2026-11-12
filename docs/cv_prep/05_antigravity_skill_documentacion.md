# DOCUMENTACIÓN Y SINCRONIZACIÓN EN LA NUBE: ANTIGRAVITY SKILL CV-INTERVIEW-DEFENSE (CV_PREP 05)

## 1. GOBERNANZA DE SINCRONIZACIÓN EN GOOGLE WORKSPACE Y DRIVE

Este documento registra la especificación y sincronización en la nube de la Antigravity Skill `cv-interview-defense`.

### 1.1 Identificadores Oficiales de la Nube
- **Google Doc Maestro Central**: `Diego Escobar - Perfil Integral y Respaldo Operativo Central`  
  - Document ID: `16qDnLxen5VduNQRqMavxM5LdfPRjBjD0mZrCjEmttlQ`
- **Google Drive — Carpeta Específica de Preparación (`CV_Prep`)**:  
  - Carpeta: `📁 CV_Prep — Diego Escobar`  
  - Folder ID: `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb`  
  - URL: `https://drive.google.com/drive/folders/17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb`
- **Documento Destino Espejo en Google Docs**:  
  - Título en la Nube: `05_antigravity_skill_documentacion`  
  - Carpeta Contenedora: `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb`  
  - Artefacto Fuente Local: `.agents/skills/cv-interview-defense/SKILL.md`  
  - Herramienta de Sincronización: `gdocs` y `scripts/sync_drive.py`

---

## 2. ESPECIFICACIÓN DE LA SKILL INTERACTIVA

La skill `cv-interview-defense` proporciona un simulador CLI interactivo (`drill_runner.py`) y un conjunto de preguntas y rúbricas STAR diseñadas para entrenar y evaluar las respuestas de Diego Escobar en entrevistas técnicas de Data Engineering y Machine Learning.

### 2.1 Componentes Principales
1. `SKILL.md`: Manifiesto y guía metodológica de la skill.
2. `scripts/drill_runner.py`: Motor de ejecución CLI con soporte para evaluación STAR y detección automatizada de penalizaciones por exageración.
3. `resources/questions_db.json`: Base de datos de preguntas categorizadas por persona (`recruiter`, `tech_lead`, `ml_researcher`, `auditor`, `technical`, `behavioral`, `executive`) y proyecto (`ontotab`, `gbm`, `ferrostats`, `sql_arena`).
4. `resources/evaluation_rubrics.json`: Rúbricas analíticas de calificación con deducciones y penalizaciones por violación de veracidad.
5. `resources/evidence_matrix.json`: Copia autoritativa de la matriz de evidencia fáctica.
6. `references/`: Guías de referencia rápida, hojas de trampa por proyecto y catálogo de antipatrones.

---

## 3. REGISTRO DE SINCRONIZACIÓN CLOUD

| Artefacto Local | Destino en Google Drive | Folder ID | Doc ID / Target | Estado de Sincronización |
|---|---|---|---|---|
| `.agents/skills/cv-interview-defense/SKILL.md` | `📁 CV_Prep — Diego Escobar` | `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb` | `05_antigravity_skill_documentacion` | Mapeado y Verificado |
| `resources/evaluation_rubrics.json` | `📁 CV_Prep — Diego Escobar` | `17keZ2p_7nWRma85Lb6HI9g5DpS2b3bAb` | `evaluation_rubrics_backup.json` | Mapeado y Verificado |

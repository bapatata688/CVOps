---
name: cv-interview-defense
description: Technical interview defense prompter and evaluation harness for Diego Escobar's master_cv.
---

# Antigravity Skill: CV Interview Defense

This skill empowers Antigravity AI agents and human evaluators to simulate, practice, and audit technical interview defense sessions for Diego Alejandro Escobar Barahona's master curriculum vitae (`master_cv`).

## Overview

In high-stakes technical interviews for Data Engineering, Cloud Infrastructure, and AI Software Engineering roles, candidate claims are subjected to rigorous behavioral, architectural, and forensic screening. This skill enforces 100% adherence to verifiable evidence, testing answers against authoritative benchmarks and penalizing unbacked exaggerations.

## Architecture & Components

The skill is organized into modular scripts, resources, and reference catalogs:

- `scripts/drill_runner.py`: High-performance Python CLI tool executing STAR drill prompts, persona-based question filtering, and automated anti-exaggeration answer scoring.
- `resources/questions_db.json`: Curated database of technical, behavioral, and audit questions spanning all four candidate projects (`ontotab`, `gbm`, `ferrostats`, `sql_arena`) and five interviewer personas (`recruiter`, `tech_lead`, `ml_researcher`, `auditor`, `executive`).
- `resources/evaluation_rubrics.json`: Formal STAR evaluation rubrics defining 1–5 scoring scales, required factual anchors, and automatic fatal penalties for seniority inflation or unbacked venue claims.
- `resources/evidence_matrix.json`: Machine-readable Single Source of Truth (SSoT) containing verified metrics, author rankings, certification IDs, and forbidden regex patterns.
- `references/question_bank.md`: Comprehensive bank of interview queries with hints and STAR answer frameworks.
- `references/scoring_rubric.md`: Detailed scoring guides and penalty thresholds for evaluators.
- `references/anti_patterns.md`: Catalog of forbidden claims, common candidate traps, and ethical boundaries.
- `references/project_cheat_sheets.md`: Quick-reference architectural cheat sheets for OntoTab, GBM, FERROSTATS, and SQL Arena.

## CLI Usage

### 1. Interactive Question Retrieval (Dry-Run)
Retrieve targeted questions for a specific interviewer persona and project:
```bash
python .agents/skills/cv-interview-defense/scripts/drill_runner.py --persona technical --project ontotab --dry-run
python .agents/skills/cv-interview-defense/scripts/drill_runner.py --persona behavioral --project gbm --dry-run
python .agents/skills/cv-interview-defense/scripts/drill_runner.py --persona executive --project ferrostats --dry-run
python .agents/skills/cv-interview-defense/scripts/drill_runner.py --persona auditor --project sql_arena --dry-run
```

### 2. Candidate Response Scoring
Evaluate a candidate STAR answer for factual completeness and anti-exaggeration compliance:
```bash
python .agents/skills/cv-interview-defense/scripts/drill_runner.py \
  --persona technical \
  --project ontotab \
  --eval-answer "Situation: In OntoTab we benchmarked 30,000 credit records using 5x3 nested CV. Task: As second author leading E01, I ran numerical baselines. Action: Evaluated XGBoost with 2,000 bootstraps. Result: Achieved 0.5596 AP, outperforming dense embeddings."
```

If the response contains forbidden claims (such as claiming lead authorship, 95% accuracy, or Senior Data Engineer status), the runner issues an immediate fatal penalty (`[FAIL]`) and exits with a non-zero code.

## Personas Supported
- `recruiter`: Assesses career narrative, communication clarity, English proficiency (EF SET C1/C2), and company fit.
- `tech_lead`: Probes database internals, concurrency (ExecutionMutex), Lakehouse design, and data quality assertions.
- `ml_researcher`: Evaluates statistical rigor, class imbalance metrics (Average Precision), and non-parametric hypothesis testing.
- `auditor`: Conducts forensic cross-examination of credentials, publication claims, and internship timelines.
- `executive`: Reviews FinOps efficiency, operational cost ($0.00/mo), and business inventory optimization (Pareto ABC).

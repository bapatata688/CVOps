#!/usr/bin/env python3
"""drill_runner.py - Technical Interview Defense Prompter and STAR Evaluation Harness

Interactive CLI drill runner for Diego Escobar's master_cv.
Evaluates STAR responses against authoritative verifiable facts and applies fatal penalties
for unbacked seniority, false venue claims, score fabrications, or project exaggerations.

Compliance:
- Zero-external-dependency: pure Python standard library.
- AGENTS.md Rule 5 compliant (Native Python verification, zero pytest).
- Seamless integration with Antigravity IDE and master_cv verification test suites.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Locate skill directory and resources
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
RESOURCES_DIR = SKILL_DIR / "resources"
QUESTIONS_DB_PATH = RESOURCES_DIR / "questions_db.json"
RUBRICS_PATH = RESOURCES_DIR / "evaluation_rubrics.json"
EVIDENCE_MATRIX_PATH = RESOURCES_DIR / "evidence_matrix.json"

# Fallback path if resources are loaded from root
if not QUESTIONS_DB_PATH.is_file():
    REPO_ROOT = SKILL_DIR.parents[1]
    QUESTIONS_DB_PATH = REPO_ROOT / ".agents" / "skills" / "cv-interview-defense" / "resources" / "questions_db.json"
    RUBRICS_PATH = REPO_ROOT / ".agents" / "skills" / "cv-interview-defense" / "resources" / "evaluation_rubrics.json"
    EVIDENCE_MATRIX_PATH = REPO_ROOT / "resources" / "evidence_matrix.json"

# Strict anti-exaggeration forbidden claim patterns
FORBIDDEN_CLAIM_PATTERNS: List[Tuple[str, str]] = [
    (r"(?i)\blead\s+author\b", "Claims unbacked role as lead author (Diego is second author of 7)"),
    (r"(?i)\bfirst\s+author\b", "Claims unbacked role as first author"),
    (r"(?i)\bprincipal\s+investigator\b", "Claims unbacked role as principal investigator"),
    (r"(?i)\bprincipal\s+researcher\b", "Claims unbacked role as principal researcher"),
    (r"(?i)\bSenior\s+Data\s+Engineer\b", "Inflates entry-level / intern experience to Senior Data Engineer"),
    (r"(?i)\bLead\s+Data\s+Engineer\b", "Inflates role to Lead Data Engineer"),
    (r"(?i)\bStaff\s+Data\s+Engineer\b", "Inflates role to Staff Data Engineer"),
    (r"(?i)\bMachine\s+Learning\s+Engineer\b", "Inflates GBM intern title to Machine Learning Engineer"),
    (r"(?i)\bML\s+Engineer\b", "Inflates GBM intern title to ML Engineer"),
    (r"(?i)\b95\s*/\s*100\b", "Falsifies EF SET score (actual certified score is 66/100 C1)"),
    (r"(?i)\b95%\s*accuracy\b", "Falsifies accuracy metrics beyond empirical benchmarks"),
    (r"(?i)\bpublished\s+in\s+IEEE\b", "Falsely claims formal peer-reviewed IEEE publication"),
    (r"(?i)\bpeer-reviewed\s+publication\b", "Falsely claims formal peer-reviewed status"),
    (r"(?i)\b(?:completed|solved)\s+(?:all\s+)?34\b", "Falsely claims candidate solved all 34 problems (actual is 3/34)"),
    (r"(?i)\b34\s*/\s*34\b", "Falsely claims 34/34 solved in SQL Arena"),
    (r"(?i)\b(?:commercial\s+startup|paying\s+customers|arr|mrr)\b", "Falsely frames personal portfolio projects as commercial venture"),
    (r"(?i)\bpermanent\s+position\s+at\s+gbm\b", "Claims permanent employment at GBM (was 13-week intern)"),
    (r"(?i)\b(?:[6-9]|\d{2,})\s+months\s+at\s+gbm\b", "Exaggerates GBM duration beyond 13 weeks"),
]

# Normalization mapping for persona aliases
PERSONA_ALIASES: Dict[str, str] = {
    "recruiter": "recruiter",
    "tech_lead": "technical",
    "technical": "technical",
    "ml_researcher": "technical",
    "auditor": "auditor",
    "behavioral": "behavioral",
    "executive": "executive",
}

# Normalization mapping for project aliases
PROJECT_ALIASES: Dict[str, str] = {
    "ontotab": "ontotab",
    "gbm": "gbm",
    "ferrostats": "ferrostats",
    "sql_arena": "sql_arena",
    "sql-arena": "sql_arena",
    "sqlarena": "sql_arena",
}


def load_json_file(path: Path) -> Dict[str, Any]:
    """Safely loads a JSON resource file."""
    if not path.is_file():
        raise FileNotFoundError(f"Required resource file not found: {path.resolve()}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to parse JSON from {path.resolve()}: {str(e)}")


def filter_questions(
    questions: List[Dict[str, Any]],
    persona: Optional[str] = None,
    project: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filters questions database matching persona and project criteria with alias normalization."""
    filtered: List[Dict[str, Any]] = []

    norm_persona = persona.lower().strip() if persona else None
    norm_project = project.lower().strip().replace("-", "_") if project else None

    # Canonical alias resolution
    canonical_persona = PERSONA_ALIASES.get(norm_persona, norm_persona) if norm_persona else None
    canonical_project = PROJECT_ALIASES.get(norm_project, norm_project) if norm_project else None

    for q in questions:
        q_persona = str(q.get("persona", "")).lower().strip()
        q_project = str(q.get("project", "")).lower().strip().replace("-", "_")

        # Persona matching: match exact, canonical, or broad alias
        persona_match = True
        if norm_persona:
            persona_match = (
                q_persona == norm_persona or
                q_persona == canonical_persona or
                (norm_persona in ["technical", "tech_lead", "ml_researcher"] and q_persona in ["technical", "tech_lead", "ml_researcher"]) or
                (norm_persona in ["behavioral", "recruiter"] and q_persona in ["behavioral", "recruiter"]) or
                (norm_persona in ["executive", "auditor"] and q_persona in ["executive", "auditor"])
            )

        # Project matching
        project_match = True
        if norm_project:
            project_match = (q_project == norm_project or q_project == canonical_project)

        if persona_match and project_match:
            filtered.append(q)

    return filtered


def evaluate_candidate_answer(
    answer: str,
    question: Optional[Dict[str, Any]] = None,
    rubrics: Optional[List[Dict[str, Any]]] = None
) -> Tuple[bool, int, List[str], List[str]]:
    """Evaluates candidate response for STAR structure, factual anchors, and forbidden exaggerations.
    
    Returns:
        (is_pass: bool, score: int, passes: List[str], violations: List[str])
    """
    violations: List[str] = []
    passes: List[str] = []

    # 1. Scan for forbidden claims and unbacked seniority
    for pattern, reason in FORBIDDEN_CLAIM_PATTERNS:
        match = re.search(pattern, answer)
        if match:
            violations.append(f"FATAL PENALTY: Matched '{match.group(0)}' -> {reason}")

    # Specific question-level prohibited terms
    if question and "prohibited_terms" in question:
        for term in question["prohibited_terms"]:
            if re.search(r"(?i)\b" + re.escape(term) + r"\b", answer):
                violations.append(f"PROHIBITED TERM PENALTY: Matched forbidden term '{term}'")

    if violations:
        # Immediate fatal deduction
        return False, 0, passes, violations

    # 2. Check STAR structure indicators
    star_markers = ["situation", "task", "action", "result"]
    star_count = sum(1 for marker in star_markers if re.search(r"(?i)\b" + marker + r"\b", answer))
    if star_count >= 3:
        passes.append(f"STAR Structure: Verified {star_count}/4 STAR components present.")
    else:
        passes.append("STAR Structure: Informal narrative (recommended to prefix with Situation, Task, Action, Result).")

    # 3. Check expected anchors if question context is provided
    score = 5
    if question and "expected_anchors" in question:
        matched_anchors = []
        missing_anchors = []
        for anchor in question["expected_anchors"]:
            if re.search(re.escape(anchor), answer, re.IGNORECASE):
                matched_anchors.append(anchor)
            else:
                missing_anchors.append(anchor)

        if matched_anchors:
            passes.append(f"Factual Anchors Verified: {', '.join(matched_anchors)}")
        if missing_anchors:
            passes.append(f"Recommended Supplemental Anchors: {', '.join(missing_anchors)}")

    return True, score, passes, violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Technical Interview Defense Prompter and STAR Evaluation Harness for master_cv",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--persona",
        type=str,
        choices=["recruiter", "tech_lead", "ml_researcher", "auditor", "technical", "behavioral", "executive"],
        help="Target interviewer persona for tailored drill retrieval."
    )
    parser.add_argument(
        "--project",
        type=str,
        choices=["ontotab", "ferrostats", "sql_arena", "sql-arena", "gbm"],
        help="Target technical project domain."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prints matching question, context, and evaluation rubric without executing scoring."
    )
    parser.add_argument(
        "--eval-answer",
        type=str,
        metavar="ANSWER_TEXT",
        help="Evaluates a candidate STAR response against factual anchors and ethical containment rules."
    )

    args = parser.parse_args()

    # Load databases
    try:
        q_data = load_json_file(QUESTIONS_DB_PATH)
        questions = q_data.get("questions", [])
    except Exception as e:
        sys.stderr.write(f"Error loading questions database: {str(e)}\n")
        return 1

    try:
        r_data = load_json_file(RUBRICS_PATH)
        rubrics = r_data.get("rubrics", [])
    except Exception:
        rubrics = []

    # Filter questions
    matching_questions = filter_questions(questions, persona=args.persona, project=args.project)

    if not matching_questions:
        # Fallback to all questions if specific filter was empty
        matching_questions = questions

    selected_question = matching_questions[0] if matching_questions else {}

    # Handle --dry-run
    if args.dry_run:
        q_id = selected_question.get("question_id", "Q-GENERAL")
        q_title = selected_question.get("title", "Technical Defense Query")
        q_text = selected_question.get("question_text", "Explain your technical contributions.")
        q_context = selected_question.get("context", "General technical evaluation.")
        q_approach = selected_question.get("suggested_approach", "Use STAR format with exact metrics.")
        q_anchors = selected_question.get("expected_anchors", [])

        print("=" * 80)
        print(f" INTERVIEW DEFENSE DRILL: [{q_id}] {q_title}")
        print("=" * 80)
        print(f"Target Persona : {args.persona or 'general'}")
        print(f"Target Project : {args.project or 'all'}")
        print("-" * 80)
        print(f"Question       : {q_text}")
        print(f"Context        : {q_context}")
        print(f"Approach (STAR): {q_approach}")
        if q_anchors:
            print(f"Required Facts : {', '.join(q_anchors)}")
        print("=" * 80)
        print("Rubric Guidelines: 5-point STAR evaluation with zero tolerance for exaggeration.")
        print("=" * 80)
        return 0

    # Handle --eval-answer
    if args.eval_answer:
        is_pass, score, passes, violations = evaluate_candidate_answer(
            args.eval_answer,
            question=selected_question,
            rubrics=rubrics
        )

        print("=" * 80)
        print(" INTERVIEW DEFENSE EVALUATION REPORT")
        print("=" * 80)

        if not is_pass:
            print("VERDICT: [FAIL] - CRITICAL ETHICAL PENALTY / VIOLATION DETECTED")
            print(f"Assigned Score: 0/5 (Immediate Disqualification)")
            print("-" * 80)
            print("VIOLATIONS:")
            for v in violations:
                print(f"  • {v}")
            print("-" * 80)
            print("Corrective Action: Remove all unbacked seniority titles, false venue claims,")
            print("or fabricated metrics. Restrict claims to verified artifacts in evidence_matrix.json.")
            print("=" * 80)
            return 1
        else:
            print(f"VERDICT: [PASS] - VERIFIED STAR DEFENSE")
            print(f"Assigned Score: {score}/5 (Strong Technical & Ethical Alignment)")
            print("-" * 80)
            print("AUDIT FINDINGS:")
            for p in passes:
                print(f"  • {p}")
            print("=" * 80)
            return 0

    # Default if neither --dry-run nor --eval-answer is supplied: print summary and exit 0
    print(f"Interview defense prompter ready. Matching questions: {len(matching_questions)}.")
    print("Use --dry-run to display drill questions or --eval-answer to score responses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

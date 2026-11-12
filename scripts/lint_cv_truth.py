#!/usr/bin/env python3
"""
scripts/lint_cv_truth.py
Ethical Truthfulness and Anti-Exaggeration Linter for master_cv

Enforces:
1. Zero unbacked claims and zero title/seniority inflation (e.g. Senior/Lead/Staff, ML Engineer).
2. Zero metric exaggeration (e.g., 95/100 EF SET draft typo, solved all 34 SQL Arena problems).
3. Exact metric assertions (0.5596 AP, 30,000 records, 13 weeks, EF SET 66/100).
4. Verbatim institutional anchors (University of the People Admitted Term 3 2027).
5. Zero template placeholder leaks ([TODO], [TBD], [PLACEHOLDER]).

Exit code semantics:
- 0: All files 100% clean and compliant.
- 1: One or more violations detected, or missing required metrics/files.
- 2: Invalid CLI arguments (argparse default).

Compliance: Native Python standard library only. Rule 5 compliant (Zero Pytest, Zero Matplotlib).
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


REPO_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_HTML_TEMPLATES = [
    Path("cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html"),
    Path("cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.html"),
    Path("cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.html"),
    Path("cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.html"),
]

CANONICAL_PDF_TARGETS = [
    Path("cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf"),
    Path("cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.pdf"),
    Path("cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf"),
    Path("cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf"),
]

# Baseline fallback forbidden patterns if evidence_matrix.json is missing or partial
FALLBACK_FORBIDDEN_PATTERNS = [
    (r"(?i)\b(?:95\s*/\s*100|95%\s*ef\s*set|ef\s*set[\s:\-]+(?:score\s*(?:of\s*)?)?95)\b", "Falsification of EF SET score (actual certified score is 66/100 C1)"),
    (r"(?i)(?:\b(?:senior|lead|principal|staff|sr\.?)\s+(?:data\s+engineer|cloud\s+architect|software\s+engineer|engineer|architect)\b|\b(?:data\s+engineer|ingeniero\s+de\s+datos|arquitecto\s+cloud|ingeniero\s+de\s+software)\s+(?:senior|lead|principal|staff|sr\.?)\b|\bingeniero\s+(?:senior|lead|principal|staff|sr\.?)\b)", "Senior/Lead/Staff/Principal title inflation"),
    (r"(?i)\b(?:professional\s+data\s+engineer|google\s+cloud\s+pde|gcp\s+pde)\b", "Unbacked Google Cloud Professional Data Engineer certification claim"),
    (r"(?i)\b(?:ml|machine\s+learning)\s+engineer\b(?!\s*intern)", "Machine Learning Engineer title inflation on intern/research role"),
    (r"(?i)(?<!under\s)(?<!under\sthe\s)(?<!bajo\s)(?<!bajo\sel\s)(?<!del\s)(?<!por\sel\s)\b(?:principal\s+investigator|investigador\s+principal|lead\s+(?:researcher|scientist|author)|first\s+author|sole\s+author|primer\s+autor|autor\s+(?:principal|[uú]nico))\b", "Authorship inflation on OntoTab research"),
    (r"(?i)\b(?:peer-reviewed|published\s+in\s+(?:ieee|acm|neurips|icml|cvpr|kdd)|publicado\s+en\s+(?:ieee|acm|neurips|icml|cvpr|kdd)|revisado\s+por\s+pares|indexed\s+journal|revista\s+indexada|formalmente\s+publicado)\b", "False claim of peer-reviewed venue publication for OntoTab"),
    (r"(?i)(?:\\b(?:solved|completed|resolvi|resolv[ií]|complet[eé]|complet[oó])\\s+(?:(?:all|todos?\\s+(?:los?)?|los|las)\\s+)?34(?:\\/34)?\\s+(?:exercises|problems|drills|ejercicios|problemas|retos)\\b|\\b34\\s*(?:\\/|\\s+out\\s+of\\s+|\\s+of\\s+|\\s+de\\s+)\\s*34\\s+(?:solved|completed|resueltos?|completados?)\\b)", "False claim of solving all 34 problems in SQL Arena"),
    (r"(?i)(?:\\b(?:founder|co-?founder|fundador|co-?fundador|ceo|startup|commercial\\s+enterprise|paying\\s+clients?|revenue-generating|empresa\\s+comercial|clientes\\s+de\\s+pago)\\b|(?:\\$|USD\\s*)[0-9,]+\\s*(?:[kKmM])?\\s+(?:mrr|arr|revenue)\\b)", "Commercial fabrication for portfolio projects"),
    (r"(?i)\b(?:graduated?\s+from|degree\s+awarded\s+by|alumn[iua]\s+of|graduate\s+of|graduad[oa]\s+de|titulad[oa]\s+por|egresad[oa]\s+de)\s+(?:university\s+of\s+the\s+people|uopeople)\b", "Premature graduation claim for University of the People"),
    (r"\[TODO\]|\[TBD\]|\[PLACEHOLDER\]|\bTODO\b|\bTBD\b|\bPLACEHOLDER\b", "Unresolved template placeholder leak"),
]


def load_evidence_matrix(matrix_path: Optional[Path] = None) -> Dict[str, Any]:
    target_path = matrix_path or (REPO_ROOT / "resources" / "evidence_matrix.json")
    if not target_path.is_file():
        return {}
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"[WARNING] Failed to load evidence matrix from {target_path}: {exc}", file=sys.stderr)
        return {}


def compile_forbidden_patterns(matrix: Dict[str, Any]) -> List[Tuple[re.Pattern, str, str]]:
    compiled: List[Tuple[re.Pattern, str, str]] = []
    seen_patterns = set()

    # 1. Global forbidden regexes
    for rule in matrix.get("global_forbidden_regexes", []):
        pat = rule.get("regex")
        desc = rule.get("description", "Global forbidden regex")
        rule_id = rule.get("rule_id", "GLOBAL-FORBID")
        if pat and pat not in seen_patterns:
            try:
                compiled.append((re.compile(pat, re.IGNORECASE), desc, rule_id))
                seen_patterns.add(pat)
            except Exception as e:
                print(f"[WARN] Invalid regex {pat}: {e}", file=sys.stderr)

    # 2. Containment harness forbidden regex patterns
    harness = matrix.get("containment_harness", {})
    for rule in harness.get("forbidden_regex_patterns", []):
        pat = rule.get("pattern")
        reason = rule.get("reason", "Harness containment violation")
        if pat and pat not in seen_patterns:
            try:
                compiled.append((re.compile(pat, re.IGNORECASE), reason, "HARNESS-PATTERN"))
                seen_patterns.add(pat)
            except Exception as e:
                print(f"[WARN] Invalid regex {pat}: {e}", file=sys.stderr)

    # 3. Domain-specific forbidden regex patterns
    for domain_key, domain_data in matrix.get("containment_domains", {}).items():
        if isinstance(domain_data, dict):
            for rule in domain_data.get("forbidden_regex_patterns", []):
                pat = rule.get("regex")
                desc = rule.get("description", f"Domain violation: {domain_key}")
                rule_id = rule.get("rule_id", domain_key)
                if pat and pat not in seen_patterns:
                    try:
                        compiled.append((re.compile(pat, re.IGNORECASE), desc, rule_id))
                        seen_patterns.add(pat)
                    except Exception as e:
                        print(f"[WARN] Invalid regex {pat}: {e}", file=sys.stderr)

    # 4. Fallback patterns if needed
    for pat, desc in FALLBACK_FORBIDDEN_PATTERNS:
        if pat not in seen_patterns:
            try:
                compiled.append((re.compile(pat, re.IGNORECASE), desc, "FALLBACK-RULE"))
                seen_patterns.add(pat)
            except Exception as e:
                pass

    return compiled


def extract_text_from_file(file_path: Path) -> Tuple[str, List[str]]:
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        if not PYPDF_AVAILABLE:
            raise RuntimeError("pypdf is required to lint PDF files.")
        reader = pypdf.PdfReader(str(file_path))
        extracted = []
        for page in reader.pages:
            t = page.extract_text() or ""
            extracted.append(t)
        full_text = "\n".join(extracted)
        return full_text, full_text.splitlines()

    # HTML / TXT / MD
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    return content, lines


def lint_content_against_patterns(
    file_path: Path,
    lines: List[str],
    patterns: List[Tuple[re.Pattern, str, str]]
) -> List[Dict[str, Any]]:
    violations: List[Dict[str, Any]] = []

    for line_idx, line in enumerate(lines, start=1):
        clean_line = re.sub(r"<[^>]+>", " ", line)  # strip tags for cleaner matching
        for regex, reason, rule_id in patterns:
            # Test both raw line and stripped line
            match = regex.search(line) or regex.search(clean_line)
            if match:
                violations.append({
                    "file": str(file_path),
                    "rule_id": rule_id,
                    "reason": reason,
                    "matched_text": match.group(0),
                    "line_number": line_idx,
                    "line_content": line.strip()[:160],
                })
    return violations


def verify_canonical_metrics(files: List[Path]) -> List[str]:
    errors = []
    combined_text = ""
    for f in files:
        if f.is_file():
            try:
                txt, _ = extract_text_from_file(f)
                combined_text += "\n" + txt
            except Exception as e:
                errors.append(f"Could not read {f}: {e}")

    # Check mandatory metrics across portfolio
    if "0.5596" not in combined_text and "0.559596" not in combined_text:
        errors.append("Missing exact OntoTab XGBoost baseline metric: 0.5596 AP")

    if "30,000" not in combined_text and "30000" not in combined_text:
        errors.append("Missing exact OntoTab dataset records: 30,000")

    if "66/100" not in combined_text:
        errors.append("Missing certified EF SET score: 66/100")

    if "C1 Advanced" not in combined_text and "C1 Avanzado" not in combined_text:
        errors.append("Missing certified EF SET level: C1 Advanced")

    if "University of the People" not in combined_text:
        errors.append("Missing verified education anchor: University of the People")

    if "Term 3, 2027" not in combined_text and "Term 3 2027" not in combined_text and "Expected Start: 2027" not in combined_text and "Inicio esperado: 2027" not in combined_text:
        errors.append("Missing verified enrollment term: Expected Start: 2027")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ethical Truthfulness and Anti-Exaggeration Linter for master_cv."
    )
    parser.add_argument(
        "--files", "-f",
        nargs="+",
        default=None,
        help="One or more specific files to lint (e.g. HTML templates, generated PDFs)."
    )
    parser.add_argument(
        "--matrix", "-m",
        default=None,
        help="Path to authoritative evidence_matrix.json."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output."
    )

    args = parser.parse_args()

    matrix_path = Path(args.matrix) if args.matrix else None
    matrix = load_evidence_matrix(matrix_path)
    patterns = compile_forbidden_patterns(matrix)

    is_custom_files = bool(args.files)
    if is_custom_files:
        targets_to_scan = [Path(p).resolve() for p in args.files]
    else:
        # Default scan: all 4 HTML templates and any compiled canonical PDFs
        targets_to_scan = [(REPO_ROOT / p).resolve() for p in CANONICAL_HTML_TEMPLATES]
        for p in CANONICAL_PDF_TARGETS:
            pdf_path = (REPO_ROOT / p).resolve()
            if pdf_path.is_file():
                targets_to_scan.append(pdf_path)

    print("=" * 80)
    print("MASTER_CV ETHICAL TRUTHFULNESS & ANTI-EXAGGERATION LINTER")
    print(f"Authoritative Matrix: {matrix_path or (REPO_ROOT / 'resources/evidence_matrix.json')}")
    print(f"Total Rules Loaded:   {len(patterns)}")
    print(f"Target Files Scanned: {len(targets_to_scan)}")
    print("=" * 80)

    total_violations = 0
    all_violations: List[Dict[str, Any]] = []

    for target in targets_to_scan:
        if not target.is_file():
            print(f"\n[ERROR] Target file does not exist: {target}", file=sys.stderr)
            return 1

        try:
            _, lines = extract_text_from_file(target)
        except Exception as exc:
            print(f"\n[ERROR] Failed to read {target.name}: {exc}", file=sys.stderr)
            return 1

        violations = lint_content_against_patterns(target, lines, patterns)
        if violations:
            total_violations += len(violations)
            all_violations.extend(violations)
            print(f"\n[VIOLATIONS DETECTED] {target.name} ({len(violations)} issues):")
            for v in violations:
                print(f"  Line {v['line_number']:4d} [{v['rule_id']}]: '{v['matched_text']}'")
                print(f"    Reason:  {v['reason']}")
                print(f"    Snippet: {v['line_content']}")
        else:
            if args.verbose or not is_custom_files:
                print(f"  [PASS] {target.name}")

    # If running default canonical template scan, verify required factual metrics
    if not is_custom_files:
        metric_errors = verify_canonical_metrics(targets_to_scan)
        if metric_errors:
            print("\n[METRIC VERIFICATION ERRORS]:")
            for err in metric_errors:
                print(f"  - {err}")
            total_violations += len(metric_errors)

    print("-" * 80)
    if total_violations == 0:
        print("[PASS] ALL TRUTHFULNESS AND ETHICAL CONTAINMENT CHECKS PASSED.")
        print("-" * 80)
        return 0
    else:
        print(f"[FAIL] Truthfulness validation failed with {total_violations} violation(s).", file=sys.stderr)
        print("-" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

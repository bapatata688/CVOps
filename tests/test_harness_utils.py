"""test_harness_utils.py - Reusable Verification Helpers for master_cv E2E Testing

Pure Python testing utilities complying with zero-pytest / zero-external-framework directives.
Provides deterministic, opaque-box helpers for:
- File and directory path validation
- Git repository status inspection
- SHA256 checksum calculation & baseline verification
- Subprocess execution with timeouts and output capture
- pypdf PDF page count, mediabox dimensions, and text extraction
- docs/DECISION_LOG.md 8-field schema parsing and validation
- Truthfulness / anti-exaggeration linter assertion helpers
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Attempt importing pypdf for PDF geometry assertions
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# Authoritative known SHA256 hashes of verified assets
KNOWN_ASSET_HASHES: Dict[str, str] = {
    "certifications/EF_SET_Certificate_C1_Advanced.pdf": "0CD51116D49A65E074C3AAC8477BFF2FA3E2725A499CFF61A1319D1BED35EE92",
    "certifications/Google_Cloud_Certified_Associate_Data_Practitioner.pdf": "D1A4A3B987E0E1B06FD48C9966B330C5B1469F74EC7B0EFC3931DE4D4F7DC3A6",
    "recommendations/Carta_Recomendacion_Diego_Escobar_ES.docx": "F5BEA59F283A575A622A79B18E7C0774BABC3F5B9455715B30812B88024C71ED",
    "recommendations/Recommendation_Letter_Diego_Escobar_EN.docx": "2356E0772336834BCCB238435934CBD3A9663B9CF6224186ECB773A939A50EB1",
    "research/ontotab/OntoTab-finaledit.pdf": "B21838BC8F189F0984EDFAAFE7809A96B9412E962FC84B6D2417DBDFC989F983",
    "cv/archive/Diego_Alejandro_Escobar_Barahona_CV_legacy_oct2026.pdf": "7EB95F09E3F9062B45867170934D72BB784C4B84327AEB319C8F95B8E6044E03",
}

# Standard 8 mandatory decision log fields
MANDATORY_DECISION_LOG_FIELDS: List[str] = [
    "entry_id",
    "timestamp",
    "component",
    "problem_statement",
    "root_cause_analysis",
    "alternatives_evaluated",
    "chosen_solution",
    "rationale",
]

# Forbidden claim patterns for ethical truthfulness auditing
DEFAULT_FORBIDDEN_PATTERNS: List[Tuple[str, str]] = [
    (r"\blead\s+author\b", "Claims unbacked role as lead author (Diego is second author)"),
    (r"\bfirst\s+author\b", "Claims unbacked role as first author"),
    (r"\bprincipal\s+investigator\b", "Claims unbacked role as principal investigator"),
    (r"\bprincipal\s+researcher\b", "Claims unbacked role as principal researcher"),
    (r"\bML\s+Engineer\b", "Inflates GBM intern title to Machine Learning Engineer"),
    (r"\bMachine\s+Learning\s+Engineer\b", "Inflates GBM intern title to Machine Learning Engineer"),
    (r"\bSenior\s+Data\s+Engineer\b", "Inflates entry-level / junior role to Senior"),
    (r"\b95\s*/\s*100\b", "Falsifies EF SET score (actual certified score is 66/100 C1)"),
    (r"\bpublished\s+in\s+IEEE\b", "Falsely claims formal peer-reviewed journal publication"),
    (r"\bpeer-reviewed\s+publication\b", "Falsely claims formal peer-reviewed status"),
    (r"\[TODO\]|\[TBD\]|\[PLACEHOLDER\]|\bTODO\b|\bTBD\b|\bPLACEHOLDER\b", "Unresolved template placeholder leak"),
]


@dataclass
class SubprocessResult:
    """Structured result of a subprocess command execution."""
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    duration_sec: float

    @property
    def success(self) -> bool:
        return self.returncode == 0


# ============================================================================
# Path & Repository Verification Helpers
# ============================================================================

def validate_path_exists(path: Union[str, Path], is_dir: bool = False) -> bool:
    """Asserts that a file or directory exists and matches expected type."""
    p = Path(path)
    if not p.exists():
        return False
    if is_dir and not p.is_dir():
        return False
    if not is_dir and not p.is_file():
        return False
    return True


def assert_path_exists(path: Union[str, Path], is_dir: bool = False, msg: Optional[str] = None):
    """Raises AssertionError if target path does not exist."""
    p = Path(path)
    target_type = "Directory" if is_dir else "File"
    if not p.exists():
        raise AssertionError(msg or f"{target_type} does not exist: {p.resolve()}")
    if is_dir and not p.is_dir():
        raise AssertionError(msg or f"Expected directory but found file: {p.resolve()}")
    if not is_dir and not p.is_file():
        raise AssertionError(msg or f"Expected file but found directory: {p.resolve()}")


def validate_git_repo(repo_dir: Union[str, Path]) -> bool:
    """Verifies that repo_dir is an initialized Git repository."""
    p = Path(repo_dir)
    git_dir = p / ".git"
    if not git_dir.exists():
        return False
    # Execute git rev-parse inside repo_dir
    res = run_command_safe(["git", "rev-parse", "--is-inside-work-tree"], cwd=str(p))
    return res.success and "true" in res.stdout.lower()


# ============================================================================
# SHA256 & Asset Checksum Helpers
# ============================================================================

def compute_sha256(filepath: Union[str, Path]) -> str:
    """Computes the uppercase hexadecimal SHA256 checksum of a file."""
    p = Path(filepath)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p.resolve()}")
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def verify_sha256(filepath: Union[str, Path], expected_hash: str) -> bool:
    """Verifies that a file matches the expected SHA256 hash (case-insensitive)."""
    actual_hash = compute_sha256(filepath)
    return actual_hash == expected_hash.strip().upper()


def assert_sha256_matches(filepath: Union[str, Path], expected_hash: str):
    """Raises AssertionError if SHA256 checksum does not match expected hash."""
    actual_hash = compute_sha256(filepath)
    expected_clean = expected_hash.strip().upper()
    if actual_hash != expected_clean:
        raise AssertionError(
            f"SHA256 mismatch for {filepath}:\n"
            f"  Expected: {expected_clean}\n"
            f"  Actual:   {actual_hash}"
        )


# ============================================================================
# Subprocess Execution Helpers
# ============================================================================

def run_command_safe(
    cmd: List[str],
    cwd: Optional[Union[str, Path]] = None,
    timeout_sec: float = 60.0,
    env: Optional[Dict[str, str]] = None
) -> SubprocessResult:
    """Executes a command safely, capturing stdout, stderr, returncode, and elapsed time."""
    start_time = time.perf_counter()
    working_dir = str(cwd) if cwd else None
    
    # Merge environment if provided
    exec_env = os.environ.copy()
    if env:
        exec_env.update(env)

    try:
        proc = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=exec_env,
            shell=False
        )
        duration = time.perf_counter() - start_time
        return SubprocessResult(
            command=cmd,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_sec=duration
        )
    except subprocess.TimeoutExpired as e:
        duration = time.perf_counter() - start_time
        return SubprocessResult(
            command=cmd,
            returncode=-1,
            stdout=e.stdout or "" if isinstance(e.stdout, str) else "",
            stderr=f"TimeoutExpired after {timeout_sec}s",
            duration_sec=duration
        )
    except Exception as e:
        duration = time.perf_counter() - start_time
        return SubprocessResult(
            command=cmd,
            returncode=-2,
            stdout="",
            stderr=f"Subprocess invocation exception: {type(e).__name__}: {str(e)}",
            duration_sec=duration
        )


# ============================================================================
# pypdf PDF Geometry & Text Inspection Helpers
# ============================================================================

def validate_pdf_geometry(
    pdf_path: Union[str, Path],
    expected_pages: int = 1,
    expected_box: Tuple[int, int] = (612, 792),
    tolerance_pt: float = 1.0,
    require_text: bool = True
) -> Dict[str, Any]:
    """Inspects a PDF using pypdf to verify exact page budget, mediabox, and text presence.
    
    Returns a dict with:
      - valid (bool)
      - page_count (int)
      - mediaboxes (list of (width, height))
      - text_length (int)
      - text_snippet (str)
      - errors (list of str)
    """
    if not PYPDF_AVAILABLE:
        raise RuntimeError("pypdf is not installed in the current Python environment.")

    p = Path(pdf_path)
    if not p.is_file():
        return {
            "valid": False,
            "page_count": 0,
            "mediaboxes": [],
            "text_length": 0,
            "text_snippet": "",
            "errors": [f"File not found: {p.resolve()}"],
        }

    errors: List[str] = []
    mediaboxes: List[Tuple[float, float]] = []
    extracted_text = ""

    try:
        reader = pypdf.PdfReader(str(p))
        page_count = len(reader.pages)
        if page_count != expected_pages:
            errors.append(f"Expected {expected_pages} page(s), but found {page_count}.")

        for idx, page in enumerate(reader.pages):
            box = page.mediabox
            w, h = float(box.width), float(box.height)
            mediaboxes.append((w, h))

            exp_w, exp_h = expected_box
            if abs(w - exp_w) > tolerance_pt or abs(h - exp_h) > tolerance_pt:
                errors.append(
                    f"Page {idx+1} mediabox mismatch: ({w:.1f}, {h:.1f}) pt vs "
                    f"expected ({exp_w}, {exp_h}) pt."
                )

            page_text = page.extract_text() or ""
            extracted_text += page_text + "\n"

        if require_text and len(extracted_text.strip()) == 0:
            errors.append("PDF contains zero extractable text (blank or unrendered raster).")

    except Exception as e:
        errors.append(f"PDF parsing error: {type(e).__name__}: {str(e)}")
        page_count = 0

    return {
        "valid": len(errors) == 0,
        "page_count": page_count,
        "mediaboxes": mediaboxes,
        "text_length": len(extracted_text),
        "text_snippet": extracted_text[:300].strip(),
        "errors": errors,
    }


def assert_pdf_geometry(
    pdf_path: Union[str, Path],
    expected_pages: int = 1,
    expected_box: Tuple[int, int] = (612, 792)
):
    """Raises AssertionError if the PDF fails 1-page geometry assertion."""
    result = validate_pdf_geometry(pdf_path, expected_pages=expected_pages, expected_box=expected_box)
    if not result["valid"]:
        error_msg = "; ".join(result["errors"])
        raise AssertionError(f"PDF geometry assertion failed for {pdf_path}: {error_msg}")


# ============================================================================
# DECISION_LOG.md 8-Field Schema Parser & Validator
# ============================================================================

def parse_decision_log(markdown_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Parses docs/DECISION_LOG.md into structured entries.
    
    Each entry is validated against the mandatory fields:
    - entry_id (e.g. LOG-001)
    - timestamp / date
    - component
    - problem_statement
    - root_cause_analysis
    - alternatives_evaluated
    - chosen_solution
    - rationale
    """
    p = Path(markdown_path)
    if not p.is_file():
        raise FileNotFoundError(f"DECISION_LOG.md not found at {p.resolve()}")

    content = p.read_text(encoding="utf-8")
    
    # Split by level 2 headings matching LOG-xxx
    log_pattern = re.compile(r"^##\s+\[?(LOG-\d{3,4})\]?[\s:–—]+(.*)$", re.MULTILINE)
    matches = list(log_pattern.finditer(content))
    
    if not matches:
        return []

    entries: List[Dict[str, Any]] = []

    for i, match in enumerate(matches):
        entry_id = match.group(1).strip()
        title = match.group(2).strip()
        start_idx = match.end()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        entry_body = content[start_idx:end_idx]

        # Extract normalized fields
        fields_found: Dict[str, str] = {
            "entry_id": entry_id,
            "title": title,
        }

        # Regex extractors for standard subheadings or list keys
        field_extractors = {
            "timestamp": r"[-*]\s+\*\*Timestamp\*\*:\s*([^\n]+)|###\s+Timestamp\s*\n+([^\n#]+)",
            "component": r"[-*]\s+\*\*Component\*\*:\s*([^\n]+)|###\s+Component\s*\n+([^\n#]+)",
            "problem_statement": r"###\s+Problem\s+Statement\s*\n+([^#]+)|[-*]\s+\*\*Problem\s+Statement\*\*:\s*([^\n]+)",
            "root_cause_analysis": r"###\s+Root\s+Cause\s+Analysis\s*\n+([^#]+)|[-*]\s+\*\*Root\s+Cause\*\*:\s*([^\n]+)",
            "alternatives_evaluated": r"###\s+Alternatives\s+Evaluated\s*\n+([^#]+)|[-*]\s+\*\*Alternatives\*\*:\s*([^\n]+)",
            "chosen_solution": r"###\s+Chosen\s+Solution\s*\n+([^#]+)|[-*]\s+\*\*Chosen\s+Solution\*\*:\s*([^\n]+)",
            "rationale": r"###\s+Rationale\s*\n+([^#]+)|[-*]\s+\*\*Rationale\*\*:\s*([^\n]+)",
            "verification_evidence": r"###\s+Verification\s+Evidence\s*\n+([^#]+)|[-*]\s+\*\*Verification\*\*:\s*([^\n]+)",
        }

        for field_name, pattern in field_extractors.items():
            field_match = re.search(pattern, entry_body, re.IGNORECASE)
            if field_match:
                val = field_match.group(1) or field_match.group(2) or ""
                fields_found[field_name] = val.strip()

        entries.append(fields_found)

    return entries


def validate_decision_log_entries(
    entries: List[Dict[str, Any]],
    required_fields: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """Validates that all parsed entries contain every required field."""
    req = required_fields or MANDATORY_DECISION_LOG_FIELDS
    errors: List[str] = []

    if not entries:
        return False, ["No decision log entries found."]

    for entry in entries:
        eid = entry.get("entry_id", "UNKNOWN")
        for field in req:
            if not entry.get(field):
                errors.append(f"Entry {eid} is missing mandatory field: '{field}'")

    return len(errors) == 0, errors


# ============================================================================
# Truthfulness Linter & Anti-Exaggeration Assertion Helpers
# ============================================================================

def scan_forbidden_claims(
    text_or_path: Union[str, Path],
    custom_patterns: Optional[List[Tuple[str, str]]] = None
) -> List[Dict[str, Any]]:
    """Scans raw text or a file for forbidden exaggeration patterns.
    
    Returns a list of violation dicts:
      - pattern: regex pattern that matched
      - reason: descriptive explanation
      - matched_text: exact substring matched
      - line_number: 1-indexed line number
      - line_content: full line text
    """
    patterns = custom_patterns or DEFAULT_FORBIDDEN_PATTERNS
    
    p = Path(text_or_path) if isinstance(text_or_path, (str, Path)) and not "\n" in str(text_or_path) and Path(text_or_path).exists() else None
    
    if p and p.is_file():
        content = p.read_text(encoding="utf-8", errors="ignore")
    else:
        content = str(text_or_path)

    violations: List[Dict[str, Any]] = []
    lines = content.splitlines()

    for line_idx, line in enumerate(lines, start=1):
        for pattern_str, reason in patterns:
            regex = re.compile(pattern_str, re.IGNORECASE)
            match = regex.search(line)
            if match:
                violations.append({
                    "pattern": pattern_str,
                    "reason": reason,
                    "matched_text": match.group(0),
                    "line_number": line_idx,
                    "line_content": line.strip()
                })

    return violations


def assert_truthful_content(
    text_or_path: Union[str, Path],
    custom_patterns: Optional[List[Tuple[str, str]]] = None
):
    """Raises AssertionError if any forbidden exaggeration pattern is found."""
    violations = scan_forbidden_claims(text_or_path, custom_patterns)
    if violations:
        details = "\n".join(
            f"  - Line {v['line_number']}: [{v['matched_text']}] -> {v['reason']}"
            for v in violations
        )
        raise AssertionError(f"Truthfulness linter found {len(violations)} violation(s):\n{details}")


# ============================================================================
# Self-Verification Unit Tests
# ============================================================================

class TestHarnessUtils(unittest.TestCase):
    """Self-test suite for verification helpers, ensuring zero defects in test tooling."""

    def test_compute_and_verify_sha256(self):
        """Tests SHA256 computation against known string hash."""
        init_file = Path(__file__).resolve().parent / "__init__.py"
        if init_file.exists():
            h = compute_sha256(init_file)
            self.assertTrue(len(h) == 64)
            self.assertTrue(verify_sha256(init_file, h))

    def test_run_command_safe(self):
        """Tests safe subprocess execution and returncode inspection."""
        res = run_command_safe([sys.executable, "-c", "print('HARNESS_OK')"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("HARNESS_OK", res.stdout)
        self.assertGreater(res.duration_sec, 0.0)

    def test_path_and_git_validators(self):
        """Tests file/directory existence and git repo validator."""
        init_file = Path(__file__).resolve().parent / "__init__.py"
        tests_dir = Path(__file__).resolve().parent
        self.assertTrue(validate_path_exists(init_file, is_dir=False))
        self.assertTrue(validate_path_exists(tests_dir, is_dir=True))
        self.assertFalse(validate_path_exists("nonexistent_path_xyz123.txt"))
        
        # Test git repo validator on coe repo
        coe_path = Path("c:/Users/Usuario/Projects/coe")
        if (coe_path / ".git").exists():
            self.assertTrue(validate_git_repo(coe_path))

    def test_pdf_geometry_validator(self):
        """Tests pypdf geometry inspection on known production PDF."""
        sample_pdf = Path("c:/Users/Usuario/Projects/coe/cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf")
        if sample_pdf.exists():
            res = validate_pdf_geometry(sample_pdf, expected_pages=1, expected_box=(612, 792))
            self.assertTrue(res["valid"], f"PDF validation errors: {res.get('errors')}")
            self.assertEqual(res["page_count"], 1)
            self.assertGreater(res["text_length"], 100)
            self.assertIn("Diego", res["text_snippet"])

        # Test failure on nonexistent PDF
        res_fail = validate_pdf_geometry("nonexistent.pdf")
        self.assertFalse(res_fail["valid"])

    def test_truth_linter_clean(self):
        """Tests truth linter on perfectly clean, compliant content."""
        clean_text = (
            "Diego Escobar\n"
            "Digital Solutions Specialist Intern at GBM (July - October 2026)\n"
            "Executed baseline raw and numeric-oracle experiments (E01) over 30,000 credit records.\n"
            "University of the People - Bachelor of Science in Computer Science - Admitted Term 3 2027\n"
            "EF SET Certificate C1 Advanced: 66/100\n"
        )
        violations = scan_forbidden_claims(clean_text)
        self.assertEqual(violations, [])

    def test_truth_linter_detects_violations(self):
        """Tests truth linter detection of unbacked seniorities and score exaggerations."""
        bad_text = (
            "Acted as lead author on the paper.\n"
            "Scored 95/100 on EF SET English exam.\n"
            "Promoted to Machine Learning Engineer at GBM.\n"
            "Senior Data Engineer leading multi-cloud architecture.\n"
            "Paper published in IEEE Transactions.\n"
            "TODO: add more achievements.\n"
        )
        violations = scan_forbidden_claims(bad_text)
        matched_patterns = [v["pattern"] for v in violations]
        self.assertTrue(any("lead" in p for p in matched_patterns))
        self.assertTrue(any("95" in p for p in matched_patterns))
        self.assertTrue(any("Machine" in p for p in matched_patterns))
        self.assertTrue(any("Senior" in p for p in matched_patterns))
        self.assertTrue(any("published" in p for p in matched_patterns))
        self.assertTrue(any("TODO" in p for p in matched_patterns))

    def test_decision_log_validation(self):
        """Tests parsing and validation of decision log entries."""
        sample_log = (
            "## LOG-001: WeasyPrint Windows dlopen Shared Library Failure\n"
            "- **Timestamp**: 2026-11-11T12:00:00Z\n"
            "- **Component**: scripts/compile_all.py\n"
            "### Problem Statement\n"
            "Direct import weasyprint fails on Windows.\n"
            "### Root Cause Analysis\n"
            "Missing libgobject-2.0-0 in standard Python path.\n"
            "### Alternatives Evaluated\n"
            "1. Install GTK manually. 2. Hybrid runner invoking weasyprint.exe.\n"
            "### Chosen Solution\n"
            "Adopt hybrid compiler executing Scoop CLI shim.\n"
            "### Rationale\n"
            "Guarantees seamless zero-config Windows execution.\n"
            "### Verification Evidence\n"
            "Compiled 4 PDFs successfully with exit code 0.\n"
        )
        temp_log_path = Path(__file__).resolve().parent / "temp_test_log.md"
        try:
            temp_log_path.write_text(sample_log, encoding="utf-8")
            entries = parse_decision_log(temp_log_path)
            self.assertEqual(len(entries), 1)
            valid, errors = validate_decision_log_entries(entries)
            self.assertTrue(valid, f"Validation errors: {errors}")
        finally:
            if temp_log_path.exists():
                temp_log_path.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)

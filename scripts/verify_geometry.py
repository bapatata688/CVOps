#!/usr/bin/env python3
"""
scripts/verify_geometry.py
Programmatic 1-Page Letter Geometry & Integrity Assertion for master_cv

Enforces:
1. Strict 1-page budget (len(reader.pages) == 1).
2. Exact US Letter mediabox dimensions (612.0 x 792.0 pt, tolerance 1.0 pt).
3. Non-empty text layer (>500 chars) and key anchor presence.
4. Native assertion and exit code semantics: 0 on complete pass, 1 on any violation.

Compliance: Native Python verification only. Prohibido pytest / Prohibido matplotlib.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import pypdf
except ImportError:
    print("[ERROR] pypdf is not installed. Please install via 'pip install pypdf>=4.0.0'.", file=sys.stderr)
    sys.exit(1)

CANONICAL_TARGETS = [
    Path("cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf"),
    Path("cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.pdf"),
    Path("cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf"),
    Path("cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf"),
]

EXPECTED_WIDTH_PT = 612.0   # 8.5 in * 72 pt/in
EXPECTED_HEIGHT_PT = 792.0  # 11.0 in * 72 pt/in
TOLERANCE_PT = 1.0


def verify_single_pdf(pdf_path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "path": pdf_path,
        "exists": False,
        "size_bytes": 0,
        "page_count": 0,
        "mediabox": None,
        "is_letter": False,
        "has_text": False,
        "char_count": 0,
        "errors": [],
        "overflow_preview": None,
    }

    if not pdf_path.exists():
        result["errors"].append(f"File not found: {pdf_path}")
        return result

    result["exists"] = True
    size = pdf_path.stat().st_size
    result["size_bytes"] = size
    if size == 0:
        result["errors"].append("File is empty (0 bytes)")
        return result

    try:
        reader = pypdf.PdfReader(str(pdf_path))
    except Exception as exc:
        result["errors"].append(f"Failed to parse PDF with pypdf: {exc}")
        return result

    pages = reader.pages
    result["page_count"] = len(pages)

    if len(pages) != 1:
        result["errors"].append(f"Page count violation: expected exactly 1 page, found {len(pages)} pages")
        if len(pages) > 1:
            try:
                page2_text = pages[1].extract_text()
                result["overflow_preview"] = page2_text[:300].strip()
            except Exception:
                result["overflow_preview"] = "(unable to extract overflow text)"

    if len(pages) >= 1:
        p0 = pages[0]
        mb = p0.mediabox
        width = float(mb.width)
        height = float(mb.height)
        result["mediabox"] = (width, height)

        width_ok = abs(width - EXPECTED_WIDTH_PT) <= TOLERANCE_PT
        height_ok = abs(height - EXPECTED_HEIGHT_PT) <= TOLERANCE_PT
        result["is_letter"] = width_ok and height_ok

        if not result["is_letter"]:
            result["errors"].append(
                f"MediaBox dimension violation: expected Letter ({EXPECTED_WIDTH_PT}x{EXPECTED_HEIGHT_PT} pt), "
                f"got ({width:.2f}x{height:.2f} pt)"
            )

        try:
            text = p0.extract_text() or ""
            result["char_count"] = len(text)
            if len(text.strip()) < 500:
                result["errors"].append(f"Text extraction warning: suspiciously low character count ({len(text)} chars)")
            else:
                result["has_text"] = True

            if "Diego Alejandro Escobar Barahona" not in text:
                result["errors"].append("Missing identity anchor: 'Diego Alejandro Escobar Barahona' not found in text")
            if "University of the People" not in text:
                result["errors"].append("Missing education anchor: 'University of the People' not found in text")
        except Exception as exc:
            result["errors"].append(f"Text extraction error: {exc}")

    return result


def verify_all(repo_root: Optional[Path] = None, files: Optional[List[Path]] = None, quiet: bool = False) -> bool:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    if files:
        targets = [f.resolve() for f in files]
    else:
        targets = [(repo_root / rel).resolve() for rel in CANONICAL_TARGETS]

    if not quiet:
        print("=" * 80)
        print("MASTER_CV GEOMETRY & INTEGRITY VERIFICATION (pypdf)")
        print(f"Repo Root: {repo_root}")
        print(f"Targets to inspect: {len(targets)}")
        print("=" * 80)

    all_passed = True
    results = []

    for target in targets:
        res = verify_single_pdf(target)
        results.append(res)
        status_label = "[PASS]" if not res["errors"] else "[FAIL]"
        if res["errors"]:
            all_passed = False

        mb_str = f"{res['mediabox'][0]:.1f}x{res['mediabox'][1]:.1f} pt" if res["mediabox"] else "N/A"
        if not quiet:
            print(f"\n{status_label} {res['path'].name}")
            print(f"       Path:       {res['path']}")
            print(f"       Size:       {res['size_bytes']:,} bytes")
            print(f"       Pages:      {res['page_count']} (expected 1)")
            print(f"       MediaBox:   {mb_str} (expected {EXPECTED_WIDTH_PT:.1f}x{EXPECTED_HEIGHT_PT:.1f} pt)")
            print(f"       Characters: {res['char_count']:,} chars extracted")

            if res["errors"]:
                print("       ERRORS DETECTED:")
                for err in res["errors"]:
                    print(f"         - [!] {err}")
                if res["overflow_preview"]:
                    print(f"       OVERFLOW TEXT ON PAGE 2 PREVIEW:")
                    print(f"         \"{res['overflow_preview']}\"")

    if not quiet:
        print("\n" + "=" * 80)
        if all_passed:
            print("[SUCCESS] All inspected PDF targets strictly conform to 1-page Letter geometry.")
            print("          - Page count: 1")
            print(f"          - MediaBox: {EXPECTED_WIDTH_PT} x {EXPECTED_HEIGHT_PT} pt (US Letter)")
            print("          - Text anchors verified: Diego Alejandro Escobar Barahona, University of the People")
            print("=" * 80)
        else:
            print("[FAILURE] One or more PDF targets violated geometry or integrity constraints.")
            print("          Remediation tips:")
            print("          1. If page count > 1, check CSS @page margins (5.4mm 13.0mm) or font-size (9.05pt).")
            print("          2. If mediabox != 612x792, check '@page { size: letter; }' in template CSS.")
            print("=" * 80)

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Verify 1-page Letter geometry for master_cv PDF targets.")
    parser.add_argument("--repo-root", type=Path, default=None, help="Root path of master_cv repo")
    parser.add_argument("--files", nargs="*", type=Path, default=None, help="Specific PDF files to inspect")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (minimal output)")
    args = parser.parse_args()

    passed = verify_all(repo_root=args.repo_root, files=args.files, quiet=args.quiet)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

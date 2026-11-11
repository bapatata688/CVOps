#!/usr/bin/env python3
"""
scripts/compile_all.py
Unified CLI Compiler Wrapper for master_cv

Compiles master_cv HTML templates into production-ready PDFs via WeasyPrint.
Optionally triggers programmatic 1-page geometry assertion with pypdf.

Usage:
    python scripts/compile_all.py --all --verify
    python scripts/compile_all.py --target de_es --verify
    python scripts/compile_all.py --html-only
    python scripts/compile_all.py --engine cli --verbose
"""

import argparse
import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cv.generate_all_cvs import TARGETS_BY_ID, compile_all
from scripts.verify_geometry import verify_all


def main():
    parser = argparse.ArgumentParser(
        description="Compile master_cv documents with WeasyPrint and verify geometry.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Targets available:
  - de_en:  Data Engineering (English)
  - de_es:  Data Engineering (Spanish)
  - pub_en: Scientific Research & Publications (English)
  - pub_es: Scientific Research & Publications (Spanish)
  - all:    All 4 production targets (default)
        """
    )
    parser.add_argument(
        "--target", "-t",
        nargs="+",
        default=None,
        help="One or more target IDs to compile (e.g., de_en de_es, or 'all'). Default: all"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Explicitly compile all 4 production targets"
    )
    parser.add_argument(
        "--verify", "-v",
        action="store_true",
        help="Run programmatic 1-page geometry and integrity verification after compilation"
    )
    parser.add_argument(
        "--engine",
        choices=["auto", "cli", "python"],
        default="auto",
        help="WeasyPrint execution engine (auto: CLI on Windows, native on Linux)"
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Generate/update HTML templates without compiling PDFs"
    )
    parser.add_argument(
        "--pdf-only",
        action="store_true",
        help="Compile PDFs from existing HTML templates without overwriting them"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed execution logging"
    )

    args = parser.parse_args()

    # Determine target list
    target_ids = []
    if args.all or not args.target:
        target_ids = ["all"]
    else:
        target_ids = args.target

    print("=" * 80)
    print("MASTER_CV COMPILATION ENGINE")
    print(f"Repo Root: {REPO_ROOT}")
    print(f"Targets:   {', '.join(target_ids)}")
    print(f"Engine:    {args.engine}")
    print(f"Verify:    {args.verify}")
    print("=" * 80)

    try:
        compiled_pdfs = compile_all(
            targets=target_ids,
            base_dir=REPO_ROOT,
            html_only=args.html_only,
            pdf_only=args.pdf_only,
            engine=args.engine,
            verbose=args.verbose,
        )
    except Exception as exc:
        print(f"\n[BUILD ERROR] Compilation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print("\n[SUCCESS] Compilation stage finished successfully.")

    if args.verify and not args.html_only:
        print("\n" + "-" * 80)
        print("Executing post-compilation geometry assertion...")
        print("-" * 80)
        passed = verify_all(repo_root=REPO_ROOT, files=compiled_pdfs)
        if not passed:
            print("\n[VERIFICATION ERROR] Geometry verification failed!", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

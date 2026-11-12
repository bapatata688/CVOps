#!/usr/bin/env python3
"""
scripts/run_ci_harness.py
Unified Local CI/CD Harness Runner for master_cv

Orchestrates sequential execution of the 4 verification pipeline stages:
1. Stage 1: lint     -> python scripts/lint_cv_truth.py
2. Stage 2: compile  -> python scripts/compile_all.py --all
3. Stage 3: geometry -> python scripts/verify_geometry.py
4. Stage 4: sync     -> python scripts/sync_drive.py --dry-run

CLI Options:
- --help: Lists stages ("lint", "compile", "geometry", "sync").
- --fail-fast: Immediately aborts pipeline execution upon first stage failure.
- --mock-fail-stage <stage>: Simulates failure at the specified stage (lint, compile, geometry, sync)
                             for testing error cascades and fast-fail aborts.
- --dry-run: Prints the stage execution plan without executing compilers or linters.
             Output contains "PLAN" and exits 0.

Exit Codes:
- 0: All pipeline stages executed and passed ("ALL CI CHECKS PASSED").
- 1: Any pipeline stage failed.
- 2: Invalid CLI argument flags.

Compliance: Native Python standard library only (Zero Pytest, Zero Matplotlib).
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

STAGES: List[Dict[str, Any]] = [
    {
        "name": "lint",
        "description": "Ethical Truthfulness and Anti-Exaggeration Linting",
        "command": [sys.executable, str(REPO_ROOT / "scripts" / "lint_cv_truth.py")],
    },
    {
        "name": "compile",
        "description": "Compile All 4 Canonical Production PDFs via WeasyPrint",
        "command": [sys.executable, str(REPO_ROOT / "scripts" / "compile_all.py"), "--all"],
    },
    {
        "name": "geometry",
        "description": "Programmatic 1-Page Letter Geometry Assertion (pypdf)",
        "command": [sys.executable, str(REPO_ROOT / "scripts" / "verify_geometry.py")],
    },
    {
        "name": "sync",
        "description": "Google Drive Artifact Discovery and Destination Mapping (Dry-Run)",
        "command": [sys.executable, str(REPO_ROOT / "scripts" / "sync_drive.py"), "--dry-run"],
    },
]


def run_stage(
    stage: Dict[str, Any],
    mock_fail_stage: Optional[str] = None
) -> Tuple[bool, str, str, float]:
    stage_name = stage["name"]

    if mock_fail_stage and mock_fail_stage.lower() == stage_name.lower():
        simulated_err = f"[MOCK ERROR] Simulated failure triggered for stage '{stage_name}'."
        return False, "", simulated_err, 0.05

    cmd = stage["command"]
    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=120.0
        )
        duration = time.perf_counter() - start_time
        success = (proc.returncode == 0)
        return success, proc.stdout, proc.stderr, duration
    except subprocess.TimeoutExpired:
        duration = time.perf_counter() - start_time
        return False, "", f"Stage '{stage_name}' timed out after 120s.", duration
    except Exception as exc:
        duration = time.perf_counter() - start_time
        return False, "", f"Subprocess invocation error in stage '{stage_name}': {exc}", duration


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified Local CI/CD Harness Runner for master_cv.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pipeline Stages Executed in Order:
  1. lint:     Ethical truthfulness linter (scripts/lint_cv_truth.py)
  2. compile:  Compile all 4 production targets (scripts/compile_all.py --all)
  3. geometry: Assert 1-page Letter geometry (scripts/verify_geometry.py)
  4. sync:     Verify Drive sync artifact mapping (scripts/sync_drive.py --dry-run)
        """
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        default=True,
        help="Abort pipeline immediately upon the first stage failure (default: True)."
    )
    parser.add_argument(
        "--mock-fail-stage",
        choices=["lint", "compile", "geometry", "sync"],
        default=None,
        help="Simulate a stage failure to test fast-fail abort mechanics."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print stage execution PLAN without invoking compilers or tools."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Display stdout/stderr streams from child processes."
    )

    args = parser.parse_args()

    # Dry-Run mode: print plan and exit 0
    if args.dry_run:
        print("=" * 80)
        print("MASTER_CV CI/CD HARNESS EXECUTION PLAN (DRY-RUN)")
        print(f"Repo Root: {REPO_ROOT}")
        print("Sequential Pipeline Stages:")
        for idx, s in enumerate(STAGES, start=1):
            cmd_str = " ".join(Path(c).name if str(c).endswith(".py") else str(c) for c in s["command"])
            print(f"  {idx}. [STAGE: {s['name']}] - {s['description']}")
            print(f"     Command: {cmd_str}")
        print("=" * 80)
        print("PLAN: All 4 stages scheduled for sequential execution. Dry-run complete.")
        return 0

    print("=" * 80)
    print("MASTER_CV UNIFIED LOCAL CI/CD HARNESS RUNNER")
    print(f"Repo Root:        {REPO_ROOT}")
    print(f"Total Stages:     {len(STAGES)} (lint, compile, geometry, sync)")
    print(f"Fail-Fast Mode:   {args.fail_fast}")
    if args.mock_fail_stage:
        print(f"Mock Fail Stage:  {args.mock_fail_stage}")
    print("=" * 80)

    overall_start = time.perf_counter()
    stage_results: Dict[str, bool] = {}
    aborted_early = False

    for s in STAGES:
        s_name = s["name"]
        print(f"\n>>> Running Stage: {s_name.upper()} ({s['description']})...")
        success, stdout, stderr, duration = run_stage(s, mock_fail_stage=args.mock_fail_stage)
        stage_results[s_name] = success

        status_tag = "PASS" if success else "FAIL"
        print(f"[STAGE: {s_name}] : {status_tag} ({duration:.2f}s)")

        if args.verbose or not success:
            if stdout.strip():
                print(f"--- STDOUT ({s_name}) ---")
                print(stdout.strip())
            if stderr.strip():
                print(f"--- STDERR ({s_name}) ---", file=sys.stderr)
                print(stderr.strip(), file=sys.stderr)

        if not success:
            print(f"\n[PIPELINE ERROR] Stage '{s_name}' FAILED with error.", file=sys.stderr)
            if args.fail_fast:
                print(f"[FAST-FAIL] Aborting subsequent stages immediately.", file=sys.stderr)
                aborted_early = True
                break

    overall_duration = time.perf_counter() - overall_start

    print("\n" + "=" * 80)
    print("MASTER_CV CI/CD EXECUTION SUMMARY")
    print(f"Elapsed Time: {overall_duration:.2f} seconds")
    print("-" * 80)
    for s in STAGES:
        s_name = s["name"]
        if s_name in stage_results:
            st = "PASS" if stage_results[s_name] else "FAIL"
            print(f"  [STAGE: {s_name:8s}] : {st}")
        else:
            print(f"  [STAGE: {s_name:8s}] : SKIPPED (due to early abort)")

    print("-" * 80)
    all_passed = (len(stage_results) == len(STAGES)) and all(stage_results.values())

    if all_passed:
        print("VERDICT: [PASS]")
        print("ALL CI CHECKS PASSED (ALL STAGES PASSED)")
        print("=" * 80)
        return 0
    else:
        print("VERDICT: [FAIL]", file=sys.stderr)
        print("[FAIL] CI pipeline checks failed.", file=sys.stderr)
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

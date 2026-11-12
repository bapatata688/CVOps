#!/usr/bin/env python3
"""run_all_e2e_tests.py - Unified E2E Test Suite Runner for master_cv

Executes the four-tier verification suite using Python's standard library unittest.
Adheres strictly to zero-pytest directives (AGENTS.md Rule 5).

Usage:
    python tests/run_all_e2e_tests.py
    python tests/run_all_e2e_tests.py --tier 1
    python tests/run_all_e2e_tests.py --tier harness
    python tests/run_all_e2e_tests.py --failfast --verbose
"""

import argparse
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure master_cv and tests are in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


TIER_MODULE_MAP: Dict[str, str] = {
    "harness": "test_harness_utils",
    "1": "test_tier1_features",
    "2": "test_tier2_boundaries",
    "3": "test_tier3_combinations",
    "4": "test_tier4_scenarios",
}

TIER_DESCRIPTIONS: Dict[str, str] = {
    "harness": "Verification Harness Utilities & Self-Tests",
    "1": "Tier 1: Feature Coverage & Contract Conformance",
    "2": "Tier 2: Boundary, Corner & Adversarial Cases",
    "3": "Tier 3: Cross-Feature Integration Combinations",
    "4": "Tier 4: Real-World Application & CI/CD Scenarios",
}


def create_tier_suite(tier_key: str, loader: unittest.TestLoader) -> Tuple[unittest.TestSuite, str]:
    """Loads tests for a given tier if available. Returns (suite, status_message)."""
    module_name = TIER_MODULE_MAP[tier_key]
    file_path = SCRIPT_DIR / f"{module_name}.py"

    if not file_path.is_file():
        # Module not yet created (planned milestone)
        return unittest.TestSuite(), f"PENDING (File not yet implemented: {file_path.name})"

    try:
        suite = loader.loadTestsFromName(f"tests.{module_name}")
        count = suite.countTestCases()
        return suite, f"LOADED ({count} test cases)"
    except Exception as e:
        # Fallback to loading directly by name
        try:
            suite = loader.loadTestsFromName(module_name)
            count = suite.countTestCases()
            return suite, f"LOADED ({count} test cases)"
        except Exception as inner_e:
            return unittest.TestSuite(), f"ERROR loading {module_name}: {inner_e}"


def run_e2e_suite(
    tier: str = "all",
    verbosity: int = 2,
    failfast: bool = False
) -> int:
    """Executes the test suite and returns POSIX exit code (0 = success, 1 = failure)."""
    start_time = time.perf_counter()
    loader = unittest.TestLoader()
    overall_suite = unittest.TestSuite()

    print("=" * 80)
    print(" master_cv E2E Verification Suite Runner")
    print(f" Target Repo: {REPO_ROOT}")
    print(f" Python:      {sys.version.split()[0]} ({sys.executable})")
    print(f" Mode:        Pure Python unittest (Zero-Pytest, Rule 5 Compliant)")
    print("=" * 80)

    selected_tiers: List[str] = []
    if tier == "all":
        selected_tiers = ["harness", "1", "2", "3", "4"]
    elif tier in TIER_MODULE_MAP:
        selected_tiers = [tier]
    else:
        print(f"[-] Unknown tier selection: '{tier}'. Valid options: {list(TIER_MODULE_MAP.keys())} or 'all'.")
        return 1

    tier_statuses: Dict[str, str] = {}
    total_test_count = 0
    load_errors: List[str] = []

    print("\n--- Test Discovery & Tier Inspection ---")
    for t_key in selected_tiers:
        tier_suite, status = create_tier_suite(t_key, loader)
        tier_statuses[t_key] = status
        if status.startswith("ERROR"):
            load_errors.append(f"Tier {t_key}: {status}")
        count = tier_suite.countTestCases()
        total_test_count += count
        overall_suite.addTest(tier_suite)
        print(f"  [{t_key.upper():>7}] {TIER_DESCRIPTIONS[t_key]:<48} -> {status}")

    print("-" * 80)
    print(f"Total Discovered Tests across selected tiers: {total_test_count}")
    print("=" * 80 + "\n")

    if total_test_count == 0:
        if load_errors:
            print("  FAILURES DETECTED IN TEST SUITE DISCOVERY:")
            for err in load_errors:
                print(f"    [-] {err}")
            print("  VERDICT: [FAIL] Test module loading errors encountered.")
            return 1
        print("[!] No active tests found to execute in selected tiers.")
        print("[*] Infrastructure verification completed: 0 failures.")
        return 0

    # Run the tests using standard library TextTestRunner
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        descriptions=True
    )
    result = runner.run(overall_suite)

    elapsed = time.perf_counter() - start_time

    # Print summary metrics banner
    print("\n" + "=" * 80)
    print(" E2E Verification Summary Metrics")
    print("=" * 80)
    print(f"  Total Tests Executed: {result.testsRun}")
    print(f"  Passed:               {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"  Failures:             {len(result.failures)}")
    print(f"  Errors:               {len(result.errors)}")
    print(f"  Skipped:              {len(result.skipped)}")
    print(f"  Execution Time:       {elapsed:.3f} seconds")
    print("-" * 80)

    if result.wasSuccessful() and len(load_errors) == 0:
        print("  VERDICT: [PASS] All executed tests passed successfully with zero errors.")
        print("=" * 80)
        return 0
    else:
        if load_errors:
            print("  FAILURES DETECTED IN TEST SUITE DISCOVERY:")
            for err in load_errors:
                print(f"    [-] {err}")
        print("  VERDICT: [FAIL] One or more test cases failed or raised errors.")
        print("=" * 80)
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run all master_cv E2E verification tests using standard library unittest."
    )
    parser.add_argument(
        "--tier",
        choices=["all", "harness", "1", "2", "3", "4"],
        default="all",
        help="Specify which tier to execute (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose test output (default: True)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Reduce verbosity"
    )
    parser.add_argument(
        "-f", "--failfast",
        action="store_true",
        help="Stop on first failure or error"
    )
    args = parser.parse_args()

    verbosity = 1 if args.quiet else (2 if args.verbose else 1)
    exit_code = run_e2e_suite(tier=args.tier, verbosity=verbosity, failfast=args.failfast)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

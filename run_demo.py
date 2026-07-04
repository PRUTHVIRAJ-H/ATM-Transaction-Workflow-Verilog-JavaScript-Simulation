#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(cmd):
    print(f"\n{'='*70}")
    print(">", " ".join(cmd))
    print(f"{'='*70}\n")

    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
    )

    if result.returncode != 0:
        print(f"\nFAILED: {' '.join(cmd)}")
        sys.exit(result.returncode)


def main():
    print("\nATM FSM Verification Demo\n")

    print("\n1. Running unit tests...")
    run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "tests",
            "-v",
        ]
    )

    print("\n2. Generating coverage report...")
    run(
        [
            sys.executable,
            "scripts/generate_coverage.py",
        ]
    )

    print("\n3. Generating dashboard...")
    run(
        [
            sys.executable,
            "scripts/generate_dashboard.py",
        ]
    )

    print("\nEverything completed successfully.\n")

    dashboard = ROOT / "reports" / "dashboard.html"

    print(f"Dashboard: {dashboard}")
    print("Open the dashboard in your browser.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


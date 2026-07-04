#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent

FILES = [
    ROOT / "reports" / "coverage.txt",
    ROOT / "reports" / "dashboard.html",
    ROOT / "reports" / "atm_waves.vcd",
    ROOT / "reports" / "summary.json",
]

for f in FILES:
    if f.exists():
        f.unlink()
        print(f"Deleted {f.relative_to(ROOT)}")

for p in ROOT.rglob("__pycache__"):
    shutil.rmtree(p)
    print(f"Deleted {p.relative_to(ROOT)}")
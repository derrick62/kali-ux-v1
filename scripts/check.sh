#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m compileall -q src tests
PYTHONPATH=src python3 -m pytest -q
ruff check src tests
ruff format --check src tests
PYTHONPATH=src python3 -m kali_ux --version
PYTHONPATH=src python3 -m kali_ux status >/dev/null

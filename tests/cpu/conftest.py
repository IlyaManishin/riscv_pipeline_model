from pathlib import Path
import pytest
from reports import reports

BENCHMARKS_DIR = Path("benchmarks")


def pytest_configure(config):

    if not BENCHMARKS_DIR.exists() or not (BENCHMARKS_DIR / "main.py").is_file():
        pytest.exit(
            f"\n[CRITICAL ERROR] Required submodule 'benchmarks' is missing or uninitialized!\n"
            f"Expected at: {BENCHMARKS_DIR.resolve()}\n"
            f"Please run: 'git submodule update --init --recursive' before running tests.",
            returncode=1
        )


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    reports.build_reports()

"""
build.py
========
Entry point. For every root in build_config.TEST_ROOTS:
  1. discover tests            (test_collect.collect_tests)
  2. compile each              (compiler.compile_test)
  3. progress bar; print only the failing test's name above it
  4. log full failure reasons (incl. which backend) to a log file
  5. print "X / Y compiled" per root, plus a grand total at the end
  6. write benches.lst per root, and tests_roots.txt in build/
"""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

import build_config as cfg
import build_paths as bpaths
from test_collect import collect_tests
from compiler import compile_test


# ------------------------------------------------------------------
# Console colors - only for the lines that matter (failures, totals)
# ------------------------------------------------------------------

RED = "\033[91m"
GREEN = "\033[32m"
RESET = "\033[0m"


def _summary_color(success: int, total: int) -> str:
    return GREEN if total > 0 and success == total else RED


# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

def setup_logger() -> logging.Logger:
    cfg.LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = cfg.LOG_DIR / datetime.now().strftime(cfg.LOG_FILENAME_FMT)

    logger = logging.getLogger("build")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)

    print(f"Log file: {log_path}")
    return logger


def _write_lines(path: Path, lines: list[str]) -> None:
    content = "\n".join(lines) + ("\n" if lines else "")
    path.write_text(content, encoding="utf-8")


# ------------------------------------------------------------------
# Per-root build
# ------------------------------------------------------------------

def build_root(root: cfg.TestRoot, logger: logging.Logger) -> tuple[int, int]:
    """Builds every test in `root`. Returns (success_count, total_count)."""
    tests = collect_tests(root.src_dir, root.out_dir)

    if not tests:
        print(f"[{root.name}] no tests found under {root.src_dir}")
        return 0, 0

    if root.out_dir.exists():
        shutil.rmtree(root.out_dir)
    root.out_dir.mkdir(parents=True, exist_ok=True)

    lst_lines: list[str] = []
    success_count = 0

    for test in tqdm(tests, desc=f"Building {root.name}", unit="test"):
        result = compile_test(test)

        if result.success:
            success_count += 1
            config = (test.out_dir / cfg.CONFIG_FILENAME).relative_to(root.out_dir)
            lst_lines.append(f"{test.name},{config}")
        else:
            tqdm.write(f"{RED}  FAILED: {test.name}{RESET}")
            logger.info(
                f"[{root.name}] FAILED {test.name} ({test.kind}, backend={result.backend}): {result.error}"
            )

    lst_path = root.out_dir / bpaths.TEST_LIST_NAME
    _write_lines(lst_path, lst_lines)

    total = len(tests)
    color = _summary_color(success_count, total)
    print(f"{color}[{root.name}] {success_count} / {total} tests compiled{RESET}")

    return success_count, total


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main() -> None:
    logger = setup_logger()

    grand_success = 0
    grand_total = 0

    for root in cfg.TEST_ROOTS:
        success, total = build_root(root, logger)
        grand_success += success
        grand_total += total

    roots_path = bpaths.BUILD_DIR / cfg.TESTS_ROOTS_FILENAME
    _write_lines(roots_path, [f"{root.name}/" for root in cfg.TEST_ROOTS])

    color = _summary_color(grand_success, grand_total)
    print("=" * 50)
    print(f"{color}TOTAL: {grand_success} / {grand_total} tests compiled{RESET}")
    logger.info(f"TOTAL: {grand_success} / {grand_total} tests compiled")


if __name__ == "__main__":
    main()

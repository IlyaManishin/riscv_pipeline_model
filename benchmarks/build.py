"""
build.py
========
Entry point. For every root in build_config.TEST_ROOTS:
  1. discover tests            (test_collect.collect_tests)
  2. compile each              (compiler.compile_test)
  3. progress bar; print only the failing test's name above it
  4. log full failure reasons (incl. which backend) to a log file
  5. print "X / Y compiled" per root, plus a grand total at the end
  6. write benches.lst per root, and a top-level tests.lst in build/
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


def _write_lst(path: Path, lines: list[str]) -> None:
    content = "\n".join(lines) + ("\n" if lines else "")
    path.write_text(content, encoding="utf-8")


def build_root(root: cfg.TestRoot, logger: logging.Logger) -> tuple[int, int, list[str]]:
    """Builds every test in `root`. Returns (success_count, total, built_dir_names)."""
    tests = collect_tests(root.src_dir, root.out_dir)

    if not tests:
        print(f"[{root.name}] no tests found under {root.src_dir}")
        return 0, 0, []

    if root.out_dir.exists():
        shutil.rmtree(root.out_dir)
    root.out_dir.mkdir(parents=True, exist_ok=True)

    lst_lines: list[str] = []
    built_dirs: list[str] = []
    success_count = 0

    for test in tqdm(tests, desc=f"Building {root.name}", unit="test"):
        result = compile_test(test)

        if result.success:
            success_count += 1
            imem = (test.out_dir / cfg.IMEM_FILENAME).relative_to(root.out_dir)
            dmem = (test.out_dir / cfg.DMEM_FILENAME).relative_to(root.out_dir)
            config = (test.out_dir / cfg.CONFIG_FILENAME).relative_to(root.out_dir)
            lst_lines.append(f"{test.name},{imem},{dmem},{config}")
            built_dirs.append(str(test.out_dir.relative_to(bpaths.BUILD_DIR)))
        else:
            tqdm.write(f"  FAILED: {test.name}")
            logger.info(
                f"[{root.name}] FAILED {test.name} ({test.kind}, backend={result.backend}): {result.error}"
            )

    lst_path = root.out_dir / bpaths.TEST_LIST_NAME
    _write_lst(lst_path, lst_lines)

    total = len(tests)
    print(f"[{root.name}] {success_count} / {total} tests compiled")

    return success_count, total, built_dirs


def main() -> None:
    logger = setup_logger()

    grand_success = 0
    grand_total = 0
    all_built_dirs: list[str] = []

    for root in cfg.TEST_ROOTS:
        success, total, built_dirs = build_root(root, logger)
        grand_success += success
        grand_total += total
        all_built_dirs.extend(built_dirs)

    tests_lst_path = bpaths.BUILD_DIR / cfg.TESTS_LIST_NAME
    _write_lst(tests_lst_path, all_built_dirs)

    print("=" * 50)
    print(f"TOTAL: {grand_success} / {grand_total} tests compiled")
    logger.info(f"TOTAL: {grand_success} / {grand_total} tests compiled")


if __name__ == "__main__":
    main()

from typing import Optional
from pathlib import Path

from benchmarks.build_paths import (BUILD_DIR, ASM_DIRNAME, C_DIRNAME, TEST_LIST_NAME)

# ============================================================
# TEST DISCOVERY
# ============================================================

def collect_tests(tests_dir: Path) -> list[tuple[str, str, Optional[str]]]:
    list_file = tests_dir / TEST_LIST_NAME
    if not list_file.exists():
        raise FileNotFoundError(list_file)

    result = []

    with open(list_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse structural record fields
            parts = [p.strip() for p in line.split(",")]
            test_name = parts[0]
            imem_path = tests_dir / parts[1]

            dmem_path = None
            if len(parts) > 2 and parts[2]:
                dmem_path = tests_dir / parts[2]

            if not imem_path.exists():
                raise FileNotFoundError(imem_path)
            if dmem_path and not dmem_path.exists():
                raise FileNotFoundError(dmem_path)

            result.append(
                (
                    test_name,
                    str(imem_path),
                    str(dmem_path) if dmem_path is not None else None,
                )
            )

    return result

# ============================================================
# TEST SUITE PREPARATION
# ============================================================

ASM_TESTS = collect_tests(BUILD_DIR / ASM_DIRNAME)
ASM_IDS = [test_item[0] for test_item in ASM_TESTS]

C_TESTS = collect_tests(BUILD_DIR / C_DIRNAME)
C_IDS = [test_item[0] for test_item in C_TESTS]


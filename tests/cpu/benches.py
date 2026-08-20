import json
from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from benchmarks.build_paths import BUILD_DIR, TEST_LIST_NAME

# ============================================================
# TEST DATA STRUCTURE
# ============================================================

@dataclass
class CpuTestConfig:
    name: str
    config_path: Path
    imem_size: int
    dmem_size: int
    max_cycles: int
    imem_path: Path
    dmem_path: Optional[Path] = None

# ============================================================
# TEST DISCOVERY UTILITIES
# ============================================================

def _parse_test_list(list_file: Path) -> list[tuple[str, Path]]:
    if not list_file.exists():
        raise FileNotFoundError(list_file)

    entries = []
    tests_dir = list_file.parent

    with open(list_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split(",")]
            test_name = parts[0]
            config_rel_path = parts[1]
            config_path = tests_dir / config_rel_path
            
            entries.append((test_name, config_path))

    return entries


def _load_test_config(test_name: str, config_path: Path) -> CpuTestConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file missing: {config_path}")

    with open(config_path, "r", encoding="utf-8") as cfg_f:
        cfg_data = json.load(cfg_f)

    required_keys = ["imem_size", "dmem_size", "max_cycles", "imem"]
    for key in required_keys:
        if key not in cfg_data:
            raise KeyError(f"Missing required parameter '{key}' in test config: {config_path}")

    test_dir = config_path.parent
    imem_path = test_dir / cfg_data["imem"]
    
    dmem_path = None
    if "dmem" in cfg_data:
        dmem_path = test_dir / cfg_data["dmem"]

    if not imem_path.exists():
        raise FileNotFoundError(f"IMEM file missing: {imem_path}")
    if dmem_path and not dmem_path.exists():
        raise FileNotFoundError(f"DMEM file missing: {dmem_path}")

    return CpuTestConfig(
        name=test_name,
        config_path=config_path,
        imem_size=int(cfg_data["imem_size"]),
        dmem_size=int(cfg_data["dmem_size"]),
        max_cycles=int(cfg_data["max_cycles"]),
        imem_path=imem_path,
        dmem_path=dmem_path
    )


def collect_tests(tests_dir: Path) -> list[CpuTestConfig]:
    list_file = tests_dir / TEST_LIST_NAME
    test_entries = _parse_test_list(list_file)

    result = []
    for test_name, config_path in test_entries:
        test_cfg = _load_test_config(test_name, config_path)
        result.append(test_cfg)

    return result

# ============================================================
# TEST SUITE PREPARATION
# ============================================================

ASM_DIRNAME = "asm"
C_DIRNAME = "C"

ASM_TESTS = collect_tests(BUILD_DIR / ASM_DIRNAME)
ASM_IDS = [test_item.name for test_item in ASM_TESTS]

C_TESTS = collect_tests(BUILD_DIR / C_DIRNAME)
C_IDS = [test_item.name for test_item in C_TESTS]
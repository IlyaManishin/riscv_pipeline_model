"""
build_config.py
================
Central place for build parameters - edit here, not in the build logic.
"""

from pathlib import Path

import build_paths as bpaths
from riscv_linker import riscv_compiler


class TestRoot:
    """One benchmark root: sources dir + build output dir."""
    __slots__ = ("name", "src_dir", "out_dir")

    def __init__(self, name: str, src_dir: Path, out_dir: Path):
        self.name = name
        self.src_dir = src_dir
        self.out_dir = out_dir


# single extension list applied to every root - a project may mix C and
# asm sources (e.g. compiled together into one binary by the gcc backend)
SOURCE_EXTENSIONS = {".c", ".s", ".asm"}

def discover_test_roots() -> list[TestRoot]:
    """Every directory directly under sources/ becomes a test root, named
    after itself, built into build/<name>/. Default backend for a root
    can be set via that root's base_config.json ("compiler" key)."""
    if not bpaths.BENCHES_DIR.exists():
        return []

    roots = []
    for entry in sorted(bpaths.BENCHES_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        roots.append(TestRoot(entry.name, entry, bpaths.BUILD_DIR / entry.name))
    return roots


TEST_ROOTS: list[TestRoot] = discover_test_roots()

DEFAULT_TEST_CONFIG = {
    "stack_size": riscv_compiler.DEFAULT_STACK_SIZE,
    "imem_size": riscv_compiler.DEFAULT_IMEM_SIZE,
    "dmem_size": riscv_compiler.DEFAULT_DMEM_SIZE,
    "max_cycles": 1_000_000,
    "compiler": "gcc",   # "gcc" (riscv_compiler) or "rars"
    "duration_scale": 1, # estimated test duration scale (1..5: 1 = fast, 5 = very long)
}

# keys recognized in config files and forwarded into a test's effective config
CONFIG_KEYS = ("stack_size", "imem_size", "dmem_size", "max_cycles", "compiler", "duration_scale")

BASE_CONFIG_FILENAME = "base_config.json"   # root-level, e.g. sources/C/base_config.json
CONFIG_FILENAME = "config.json"             # project-level, inside a project subfolder

PROJECT_PREFIX = "pr_"

IMEM_FILENAME = "imem.bin"
DMEM_FILENAME = "dmem.bin"
RESULT_FILENAME = "res.bin"

# RARS backend settings
RARS_PATH = bpaths.ROOT_DIR / "bin" / "rars1_6.jar"
RARS_TIMEOUT_SECONDS = 60

LOG_DIR = bpaths.BUILD_DIR / "logs"
LOG_FILENAME_FMT = "build_%Y%m%d_%H%M%S.log"

# top-level list of test root directories (e.g. "C/", "asm/")
TESTS_ROOTS_FILENAME = "tests_roots.txt"
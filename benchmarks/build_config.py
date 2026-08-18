"""
build_config.py
================
Central place for build parameters - edit here, not in the build logic.
"""

from pathlib import Path

import build_paths as bpaths
from riscv_linker import riscv_compiler


class TestRoot:
    """One benchmark root: sources dir, build output dir, source extensions."""
    __slots__ = ("name", "src_dir", "out_dir", "extensions")

    def __init__(self, name: str, src_dir: Path, out_dir: Path, extensions: set[str]):
        self.name = name
        self.src_dir = src_dir
        self.out_dir = out_dir
        self.extensions = extensions


C_EXTENSIONS = {".c"}
ASM_EXTENSIONS = {".s", ".asm"}

TEST_ROOTS: list[TestRoot] = [
    TestRoot("C", bpaths.BENCHES_DIR / bpaths.C_DIRNAME, bpaths.C_BUILD_DIR, C_EXTENSIONS),
    # riscv_compiler can assemble .s via gcc, but RARS' own runtime (ecall
    # syscalls, its pseudo-op dialect) isn't implemented by start.s/riscv.ld.
    # Trying it here - verify results before relying on it.
    TestRoot("asm", bpaths.BENCHES_DIR / bpaths.ASM_DIRNAME, bpaths.ASM_BUILD_DIR, ASM_EXTENSIONS),
]

DEFAULT_TEST_CONFIG = {
    "stack_size": riscv_compiler.DEFAULT_STACK_SIZE,
    "imem_size": riscv_compiler.DEFAULT_IMEM_SIZE,
    "dmem_size": riscv_compiler.DEFAULT_DMEM_SIZE,
    "max_cycles": 1_000_000,
}

# keys recognized in config files and forwarded into a test's effective config
CONFIG_KEYS = ("stack_size", "imem_size", "dmem_size", "max_cycles")

BASE_CONFIG_FILENAME = "base_config.json"   # root-level, e.g. sources/C/base_config.json
CONFIG_FILENAME = "config.json"             # project-level, inside a project subfolder
IGNORE_FILENAME = "ignore.json"             # root-level ignore list
PROJECT_PREFIX = "pr_"

IMEM_FILENAME = "imem.bin"
DMEM_FILENAME = "dmem.bin"
RESULT_FILENAME = "res.bin"

LOG_DIR = bpaths.BUILD_DIR / "logs"
LOG_FILENAME_FMT = "build_%Y%m%d_%H%M%S.log"

# aggregated list of every built test folder across all roots
TESTS_LIST_NAME = "tests.lst"

"""
compiler.py
===========
Adapter between a TestCase and riscv_compiler. Compiles, writes the
per-test config.json on success, captures riscv_compiler's stdout
diagnostics into a short error string on failure (it only prints and
returns a bool, no error text).
"""

from __future__ import annotations

import contextlib
import io
import json
from dataclasses import dataclass

import build_config as cfg
from riscv_linker import riscv_compiler
from test_collect import TestCase


@dataclass
class CompileResult:
    success: bool
    error: str = ""


def _write_output_config(test: TestCase) -> None:
    payload = dict(test.config)
    payload["sources"] = [f.name for f in test.sources]

    config_path = test.out_dir / cfg.CONFIG_FILENAME
    content = json.dumps(payload, indent=2)
    config_path.write_text(content, encoding="utf-8")


def compile_test(test: TestCase) -> CompileResult:
    if not test.sources:
        return CompileResult(success=False, error="no source files found")

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        try:
            success = riscv_compiler.compile_riscv(
                src_files=test.sources,
                target_dir=test.out_dir,
                imem_size=test.config["imem_size"],
                dmem_size=test.config["dmem_size"],
                stack_size=test.config["stack_size"],
            )
        except Exception as exc:
            # a single broken test must not kill the whole build
            return CompileResult(success=False, error=f"exception: {exc}")

    if not success:
        message = captured.getvalue().strip() or "compilation failed"
        return CompileResult(success=False, error=message)

    _write_output_config(test)
    return CompileResult(success=True)

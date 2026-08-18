"""
compiler.py
===========
Compiles a TestCase using the backend picked by its "compiler" config
field ("gcc" by default, or "rars"). Both backends share the same
CompileResult contract and output config.json writer below.
"""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

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


# ------------------------------------------------------------------
# gcc backend (via riscv_compiler)
# ------------------------------------------------------------------

def _compile_gcc(test: TestCase) -> CompileResult:
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


# ------------------------------------------------------------------
# rars backend
# ------------------------------------------------------------------

# RARS segment -> output filename dumped for that segment
_RARS_DUMP_TARGETS = {
    ".text": cfg.IMEM_FILENAME,
    ".data": cfg.DMEM_FILENAME,
}


def _rars_command(sources: list[Path], dump_files: dict[str, Path]) -> list[str]:
    if str(cfg.RARS_PATH).endswith(".jar"):
        cmd = ["java", "-jar", str(cfg.RARS_PATH)]
    else:
        cmd = [str(cfg.RARS_PATH)]

    cmd += ["a", "nc"] + [str(f) for f in sources]

    for segment, output_file in dump_files.items():
        cmd += ["dump", segment, "Binary", str(output_file)]

    return cmd


def _compile_rars(test: TestCase) -> CompileResult:
    test.out_dir.mkdir(parents=True, exist_ok=True)
    dump_files = {seg: test.out_dir / name for seg, name in _RARS_DUMP_TARGETS.items()}
    cmd = _rars_command(test.sources, dump_files)

    try:
        result = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=cfg.RARS_TIMEOUT_SECONDS,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return CompileResult(success=False, error="RARS timed out")
    except FileNotFoundError:
        return CompileResult(success=False, error=f"RARS not found at: {cfg.RARS_PATH}")

    # RARS reports assembler errors on stdout, not stderr
    if result.stdout.strip():
        for f in dump_files.values():
            if f.exists() and f.stat().st_size == 0:
                f.unlink()
        return CompileResult(success=False, error=result.stdout.strip())

    missing = [seg for seg, f in dump_files.items() if not f.exists()]
    if missing:
        return CompileResult(success=False, error=f"missing dump(s): {', '.join(missing)}")

    _write_output_config(test)
    return CompileResult(success=True)


# ------------------------------------------------------------------
# dispatch
# ------------------------------------------------------------------

_BACKENDS = {
    "gcc": _compile_gcc,
    "rars": _compile_rars,
}

DEFAULT_BACKEND = "gcc"


def compile_test(test: TestCase) -> CompileResult:
    if not test.sources:
        return CompileResult(success=False, error="no source files found")

    backend_name = test.config.get("compiler", DEFAULT_BACKEND)
    backend = _BACKENDS.get(backend_name)
    if backend is None:
        return CompileResult(success=False, error=f"unknown compiler backend: {backend_name}")

    return backend(test)

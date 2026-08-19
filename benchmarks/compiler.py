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
    backend: str = ""
    error: str = ""


def _write_output_config(test: TestCase) -> None:
    payload = dict(test.config)
    payload["sources"] = [f.name for f in test.sources]

    imem_path = test.out_dir / cfg.IMEM_FILENAME
    if imem_path.exists():
        payload["imem"] = cfg.IMEM_FILENAME

    dmem_path = test.out_dir / cfg.DMEM_FILENAME
    if dmem_path.exists():
        payload["dmem"] = cfg.DMEM_FILENAME

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
            return CompileResult(success=False, backend="gcc", error=f"exception: {exc}")

    if not success:
        message = captured.getvalue().strip() or "compilation failed"
        return CompileResult(success=False, backend="gcc", error=message)

    _write_output_config(test)
    return CompileResult(success=True, backend="gcc")


# ------------------------------------------------------------------
# rars backend
# ------------------------------------------------------------------

def _rars_base_command(sources: list[Path]) -> list[str]:
    if str(cfg.RARS_PATH).endswith(".jar"):
        cmd = ["java", "-jar", str(cfg.RARS_PATH)]
    else:
        cmd = [str(cfg.RARS_PATH)]
    return cmd + ["a", "nc"] + [str(f) for f in sources]


def _run_rars(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=cfg.RARS_TIMEOUT_SECONDS,
        text=True,
    )


def _compile_rars(test: TestCase) -> CompileResult:
    test.out_dir.mkdir(parents=True, exist_ok=True)
    imem_path = test.out_dir / cfg.IMEM_FILENAME
    dmem_path = test.out_dir / cfg.DMEM_FILENAME

    try:
        # .text is required - a real assembly error means it won't be produced
        text_cmd = _rars_base_command(test.sources) + ["dump", ".text", "Binary", str(imem_path)]
        text_result = _run_rars(text_cmd)
    except subprocess.TimeoutExpired:
        return CompileResult(success=False, backend="rars", error="RARS timed out")
    except FileNotFoundError:
        return CompileResult(success=False, backend="rars", error=f"RARS not found at: {cfg.RARS_PATH}")

    if not imem_path.exists() or imem_path.stat().st_size == 0:
        message = text_result.stdout.strip() or text_result.stderr.strip() or "assembly failed"
        if imem_path.exists():
            imem_path.unlink()
        return CompileResult(success=False, backend="rars", error=message)

    # .data is best-effort: many asm tests have no data section at all,
    # RARS then refuses to dump it - that is not a build failure
    try:
        data_cmd = _rars_base_command(test.sources) + ["dump", ".data", "Binary", str(dmem_path)]
        _run_rars(data_cmd)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    if dmem_path.exists() and dmem_path.stat().st_size == 0:
        dmem_path.unlink()

    _write_output_config(test)
    return CompileResult(success=True, backend="rars")


# ------------------------------------------------------------------
# dispatch
# ------------------------------------------------------------------

_BACKENDS = {
    "gcc": _compile_gcc,
    "rars": _compile_rars,
}

DEFAULT_BACKEND = "gcc"


def compile_test(test: TestCase) -> CompileResult:
    backend_name = test.config.get("compiler", DEFAULT_BACKEND)

    if not test.sources:
        return CompileResult(success=False, backend=backend_name, error="no source files found")

    backend = _BACKENDS.get(backend_name)
    if backend is None:
        return CompileResult(success=False, backend=backend_name, error=f"unknown compiler backend: {backend_name}")

    return backend(test)

"""
test_collect.py
================
Discovers benchmark tests under a test root and resolves their config.
No compilation happens here - just a list of ready-to-build TestCase objects.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import build_config as cfg


@dataclass
class TestCase:
    name: str                  # output dir name (pr_-prefixed for projects)
    kind: str                  # "simple" | "project"
    sources: list[Path]
    out_dir: Path
    config: dict = field(default_factory=dict)


# ------------------------------------------------------------------
# JSON helpers
# ------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _extract_config_values(raw: dict) -> dict:
    return {k: raw[k] for k in cfg.CONFIG_KEYS if k in raw}


def _merge_configs(*configs: dict) -> dict:
    """Later configs override earlier ones, key by key."""
    merged: dict = {}
    for c in configs:
        merged.update(c)
    return merged


# ------------------------------------------------------------------
# Ignore handling
# ------------------------------------------------------------------

def _resolve_ignore_set(root: Path, entries: list[str]) -> set[Path]:
    return {(root / entry).resolve() for entry in entries}


def _is_ignored(path: Path, root: Path, ignored: set[Path]) -> bool:
    """True if path or any ancestor up to root is in ignored."""
    try:
        rel_parts = path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        return False
    cur = root.resolve()
    for part in rel_parts:
        cur = cur / part
        if cur in ignored:
            return True
    return False


# ------------------------------------------------------------------
# Project (multi-file) test discovery
# ------------------------------------------------------------------

def _discover_project_sources(project_dir: Path, extensions: set[str]) -> tuple[list[Path], dict]:
    """Returns (source files, raw project config.json content)."""
    raw_cfg = _load_json(project_dir / cfg.CONFIG_FILENAME)

    explicit_files = raw_cfg.get("files")
    if explicit_files:
        sources = [(project_dir / rel).resolve() for rel in explicit_files]
        sources = [f for f in sources if f.exists()]
        return sorted(sources), raw_cfg

    ignored = _resolve_ignore_set(project_dir, raw_cfg.get("ignore", []))
    sources = [
        f for f in project_dir.rglob("*")
        if f.is_file()
        and f.suffix.lower() in extensions
        and not _is_ignored(f, project_dir, ignored)
    ]
    return sorted(sources), raw_cfg


# ------------------------------------------------------------------
# Root-level discovery
# ------------------------------------------------------------------

def collect_tests(root: Path, out_root: Path, extensions: set[str]) -> list[TestCase]:
    """Discover tests directly under `root`.

    A loose source file -> "simple" test. A subdirectory -> "project" test,
    sources discovered recursively unless its config.json sets "files".
    Returns [] if `root` doesn't exist; caller logs that.
    """
    if not root.exists():
        return []

    root_cfg = _extract_config_values(_load_json(root / cfg.BASE_CONFIG_FILENAME))
    root_ignore = _resolve_ignore_set(
        root, _load_json(root / cfg.IGNORE_FILENAME).get("ignore", [])
    )

    tests: list[TestCase] = []

    for entry in sorted(root.iterdir()):
        if entry.name in (cfg.IGNORE_FILENAME, cfg.BASE_CONFIG_FILENAME):
            continue
        if _is_ignored(entry, root, root_ignore):
            continue

        if entry.is_file() and entry.suffix.lower() in extensions:
            name = entry.stem
            effective = _merge_configs(cfg.DEFAULT_TEST_CONFIG, root_cfg)
            tests.append(TestCase(
                name=name,
                kind="simple",
                sources=[entry],
                out_dir=out_root / name,
                config=effective,
            ))

        elif entry.is_dir():
            sources, raw_proj_cfg = _discover_project_sources(entry, extensions)
            proj_cfg = _extract_config_values(raw_proj_cfg)
            effective = _merge_configs(cfg.DEFAULT_TEST_CONFIG, root_cfg, proj_cfg)
            name = f"{cfg.PROJECT_PREFIX}{entry.name}"
            tests.append(TestCase(
                name=name,
                kind="project",
                sources=sources,          # may be empty -> reported as failure downstream
                out_dir=out_root / name,
                config=effective,
            ))

    return tests

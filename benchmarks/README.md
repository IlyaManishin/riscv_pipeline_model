# RISC-V Test Compilation Subsystem (Benchmarks Builder)

This subsystem provides automated toolchain infrastructure designed to discover, compile, link, and format Assembly (ASM) and C test suites into standalone raw binary images for a Harvard-architecture RISC-V (RV32I) simulation framework.

---

## 📂 Directory Structure

```text
benchmarks/
├── sources/                          # Source files of the test suites
│   ├── asm/                          # Raw assembly tests (.s, .asm)
│   │   └── base_config.json          # (optional) root-level defaults/ignore for this suite
│   └── C/                            # C source benchmarks (.c)
│       └── base_config.json          # (optional) root-level defaults/ignore for this suite
│
├── build/                            # Generated binary artifacts (automated, gitignored)
│   ├── logs/                         # One timestamped log file per build run
│   ├── asm/                          # Built assembly tests + benches.lst
│   ├── C/                            # Built C tests/projects + benches.lst
│   └── tests_roots.txt               # List of every discovered test root (e.g. "C/", "asm/")
│
├── riscv_linker/                     # Bare-metal C linker
│   ├── linker/
│   │   ├── riscv.ld                  # Linker script defining memory topology
│   │   └── start.s                   # CRT0 assembly initialization routine
│   └── riscv_compiler.py             # gcc-based compile/link/objcopy pipeline
│
├── bin/
│   └── rars1_6.jar                   # RARS (RISC-V Assembler and Runtime Simulator)
│
├── config_templates/                 # Documentation-only templates (not read by the code)
│   ├── base_config.template.jsonc    # every recognized root-level field, commented out
│   └── config.template.jsonc         # every recognized project-level field, commented out
│
├── legacy /                          # Deprecated scripts, kept for reference only
│   └── RARS_compiler.py              # superseded by compiler.py's "rars" backend
│
├── build_paths.py                    # Centralized project path mapping
├── build_config.py                   # All tunable build parameters (single source of truth)
├── test_collect.py                   # Test discovery: scans a root, resolves config, returns TestCase list
├── compiler.py                       # Compiles a TestCase via the "gcc" or "rars" backend
├── build.py                          # Master build - entry point
└── README.md
```

---

## ⚙️ Architectural Design & Memory Mapping

The build system strictly segregates compiled test execution spaces to comply with a Harvard-architecture memory organization. Output images are cleaved into two independent, unformatted byte streams:

1. **Instruction Memory (`imem.bin`)** — the executable `.text` segment.
   * Base Address (`ORIGIN`): `0x40000000`
   * Base Capacity (`LENGTH`): `32 KB` (32768 bytes) by default, overridable per test (see [Configuration](#-configuration)).

2. **Data Memory (`dmem.bin`)** — static data allocations, literal pools, initialized/uninitialized variables, and the runtime stack (`.rodata`, `.data`, `.sdata`, `.bss`).
   * Base Address (`ORIGIN`): `0x80000000`
   * Base Capacity (`LENGTH`): `16 KB` (16384 bytes) by default, overridable per test.

### 🏁 Architectural Verification Protocol (Signature)

Test tracking and execution termination validation rely on a dedicated hardware register interface. General-purpose register **`x31`** (`TEST_RESULT`) is reserved as an architectural verification signature monitored by the simulation environment:

* `0` (`CpuTestResult.TEST_RUN`) — Program execution in progress.
* `1` (`CpuTestResult.TEST_PASS`) — Execution concluded; test criteria satisfied.
* `2` (`CpuTestResult.TEST_FAIL`) — Functional failure detected during execution.

---

## 🔍 Test Discovery

**Test roots are discovered automatically.** `build_config.discover_test_roots()` scans `sources/` once at startup: every non-hidden subdirectory found there becomes a test root, named after itself, built into `build/<name>/` (currently `asm/` and `C/` - add another folder under `sources/` and it's picked up on the next run, nothing to register by hand). To exclude something from `sources/` entirely, don't put it there - a folder that shouldn't be scanned as tests doesn't belong under `sources/` in the first place.

Within a test root, `test_collect.py` produces two kinds of tests:

* **Simple test** — a loose source file directly inside the root (e.g. `sources/C/foo.c`). Compiled on its own. Output goes to `build/C/foo/`.
* **Project test** — a subdirectory inside the root (e.g. `sources/C/my_project/`). All matching source files inside it are discovered recursively and compiled together as one unit (C and asm files may be mixed in the same project). Output goes to `build/C/pr_my_project/` — the `pr_` prefix makes project outputs easy to spot next to simple-test outputs.

Recognized source extensions are defined once, for every root, in `build_config.SOURCE_EXTENSIONS` (`.c`, `.s`, `.asm`).

---

## 🧩 Configuration

Every test gets an **effective config** made of `stack_size`, `imem_size`, `dmem_size`, `max_cycles`, and `compiler`. It is resolved by merging, in increasing priority:

1. built-in defaults (`build_config.DEFAULT_TEST_CONFIG`)
2. `base_config.json` at the root of a test suite (e.g. `sources/C/base_config.json`)
3. `config.json` inside a project folder (project tests only)

Only fields actually present in a config file override the previous level - anything omitted is inherited. See `config_templates/` for every recognized field, documented and commented out.

* **`base_config.json`** (root level) may also set `"ignore"`: a list of files/folders (relative to the root) to skip entirely - both loose test files and whole project folders. This is the only place root-level exclusions live; there is no separate ignore file for `sources/` itself.
* **`config.json`** (project level) may set `"ignore"` the same way (relative to the project folder), or `"files"` - an explicit list of source files to compile, which bypasses auto-discovery and `"ignore"` entirely.
* **`"compiler"`** selects the backend: `"gcc"` (default, via `riscv_compiler`) or `"rars"`. It can be set at any of the three levels above, e.g. to make an entire `asm/` suite build with RARS while `C/` stays on gcc, or to flip a single project.
* **`"duration_scale"`** specifies an estimated execution time rating for the test on a integer scale from 1 to 5 (1 = fast/short, 5 = very long). Defaults to `1` if omitted across configs.

Every successfully built test gets its own `config.json` written into its output folder: the effective config that was actually used, the list of compiled source files as paths relative to the test's own folder (so a project's nested layout, e.g. `core/algo.c`, is preserved rather than flattened to a bare filename), and - only if the file was actually produced - `"imem"`/`"dmem"` pointing at `imem.bin`/`dmem.bin` in that same folder. A missing key means the file doesn't exist (e.g. no data section was assembled), rather than pointing at a binary that isn't there.

---

## 🛠️ Compilation Backends (`compiler.py`)

`compiler.py` exposes a single entry point, `compile_test(test)`, which dispatches to one of two backends based on the test's effective `"compiler"` value.

### `gcc` backend (default)

Uses `riscv_linker/riscv_compiler.py`, a `riscv64-unknown-elf-gcc` cross-compilation pipeline:

* **Low-Level Initialization (`start.s`)**: Establishes the execution entry point (`_start`), sets up `gp`/`sp`, and zero-initializes `.bss` before calling `main`.
* **Linker Script (`riscv.ld`)**: Controls memory section alignment and stack placement, parameterized by the effective `stack_size`/`imem_size`/`dmem_size`.
* **Binary Extraction**: Compiles with `-ffreestanding -nostdlib` and uses `objcopy` to split the output: `-j .text` → `imem.bin`, `-R .text` → `dmem.bin` (best-effort - a project with no data segment simply won't get a `dmem.bin`).

### `rars` backend

Invokes `bin/rars1_6.jar` directly. `.text` is dumped to `imem.bin` and is the only required output - a real assembly error is detected by its absence. `.data` is dumped to `dmem.bin` on a best-effort basis: many asm tests have no data section, and RARS refusing to dump an empty segment is not treated as a build failure.

> RARS provides its own runtime (`ecall` syscalls, its own pseudo-op dialect) that the gcc/bare-metal pipeline does not implement. Sources written against RARS-specific behaviour should stay on the `rars` backend; only switch a suite to `gcc` after confirming it doesn't depend on that runtime.

---

## 📝 Manifest Generation

* **`benches.lst`** — one per test root (e.g. `build/C/benches.lst`), rewritten from scratch after every build of that root:

  ```text
  <test_name>,<relative_path_to_config>
  ```

  Only the test name and a path to its `config.json` - no imem/dmem paths here anymore, since not every test produces a `dmem.bin`. Read `imem`/`dmem` out of the referenced `config.json` instead (see [Configuration](#-configuration)).

* **`tests_roots.txt`** — one file at `build/tests_roots.txt`, listing every discovered test root (`C/`, `asm/`, ...). Unlike `benches.lst`, it is never rewritten wholesale: each run only *adds* roots it discovered but doesn't find in the file yet (prepended to the top), existing lines are left as-is - so a filtered run (`test_root=C`) doesn't wipe out entries for roots it didn't touch.

Both are parsed natively by test benches (`pytest`) to dynamically parameterize execution targets.

---

## 🪵 Logging

Each run of `build.py` writes a timestamped log file to `build/logs/build_<timestamp>.log`. Only failures are logged (successful builds aren't, to keep the log focused), one line per failure with the test name, its kind (`simple`/`project`), the backend that was used, and the error. The console mirrors this with just the failing test's name printed above the progress bar (bright red), plus a final `X / Y compiled` summary per root and overall (green if everything built, red otherwise). Pass `--errors` to also print each failure's error text in the console, dimmed, right under its name - the log file always has it regardless of this flag.

---

## 🚀 Execution

Run the master script from `benchmarks/`:

```bash
python build.py
```

This builds every discovered test root. Optional arguments:

```bash
python build.py test_root=C          # build only the "C" root
python build.py --errors             # also print each failure's error text (dimmed) in the console
python build.py test_root=asm --errors
```

`test_root=<name>` doesn't change how a root is built - it still reads that root's `base_config.json`/`config.json` exactly like a full run, it just narrows which roots the loop iterates over. An unknown name prints the available roots and exits without building anything.

For each root built, the script clears `build/<root>/`, discovers and compiles every test, prints/logs a live progress bar with a per-root and total success count, and writes out that root's `benches.lst`. `build/tests_roots.txt` is updated (not overwritten) after every run, regardless of `test_root=`.
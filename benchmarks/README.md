# RISC-V Test Compilation Subsystem (Benchmarks Builder)

This subsystem provides automated toolchain infrastructure designed to compile, link, and format Assembly (ASM) and C test suites into standalone raw binary images for a Harvard-architecture RISC-V (RV32I) simulation framework.

---

## 📂 Directory Structure

```text
benchmarks/
├── sources/               # Source files of the test suites
│   ├── asm/               # Raw assembly tests (.s, .S, .asm)
│   └── C/                 # Target C source benchmarks (.c)
│
├── build/                 # Generated binary artifacts (automated)
│   ├── asm/               # Formatted binaries for assembly tests
│   └── C/                 # Formatted binaries for C benchmarks
│
├── riscv_linker/          # Bare-metal C linker
│   ├── linker/
│   │   ├── riscv.ld       # Linker script defining memory topology
│   │   └── start.s        # CRT0 assembly initialization routine
│   └── Makefile           # GNU Cross-Compiler compilation orchestration
│
├── build_paths.py         # Centralized project path mapping
├── build.py               # Master build
├── c_compiler.py          # Compilation  driver for C scripts
├── RARS_compiler.py        # Compilation driver for ASM scripts
└── rars1_6.jar            # RARS (RISC-V Assembler and Runtime Simulator)

```

---

## ⚙️ Architectural Design & Memory Mapping

The build system strictly segregates compiled test execution spaces to comply with a Harvard-architecture memory organization. Output images are cleaved into two independent, unformatted byte streams:

1. **Instruction Memory (`imem.bin`)** Contains the executable `.text` segment.
* Base Address (`ORIGIN`): `0x40000000`
* Base Capacity (`LENGTH`): `32 KB` (32768 bytes)


2. **Data Memory (`dmem.bin`)** Consolidates static data allocations, literal pools, initialized variables, uninitialized blocks, and runtime stack spaces (`.rodata`, `.data`, `.sdata`, `.bss`).
* Base Address (`ORIGIN`): `0x80000000`
* Base Capacity (`LENGTH`): `16 KB` (16384 bytes)



### 🏁 Architectural Verification Protocol (Signature)

Test tracking and execution termination validation rely on a dedicated hardware register interface. General-purpose register **`x31`** (`TEST_RESULT`) is reserved as an architectural verification signature monitored by the simulation environment:

* `0` (`CpuTestResult.TEST_RUN`) — Program execution in progress.
* `1` (`CpuTestResult.TEST_PASS`) — Execution concluded; test criteria satisfied.
* `2` (`CpuTestResult.TEST_FAIL`) — Functional failure detected during execution.

---

## 🛠️ Compilation Pipelines

### 1. Assembly compile (`RARS_compiler.py`)

* Recursively enumerates source files within `sources/asm/`.
* Invokes the `RARS` assembler command-line interface.
* Extracts the `.text` segment in raw binary (`Binary`) representation to generate `imem.bin`.
* Empties or discards unutilized memory segments if data structures are omitted.

### 2. C compile (`c_compiler.py`)

Compiling high-level C programs down to target execution binaries utilizes a `riscv64-unknown-elf-gcc` cross-compilation pipeline:

* **Low-Level Initialization (`start.s`)**: Establishes the execution entry point (`_start`). Configures the global pointer (`gp` using `__global_pointer$`) and seeds the stack pointer (`sp` targeting `__stack_top`). Executes an unrolled initialization loop to clear (zero-initialize) the static `BSS` memory boundary prior to calling `main`.
* **Linker Distribution (`riscv.ld`)**: Explicitly controls memory section alignment. Sets an isolated hardware stack space boundary (`STACK_SIZE = 128 bytes`) at the top boundary of `dmem`.
* **Binary Extraction (`Makefile`)**: Compiles the source unit alongside the runtime assembly file utilizing optimization and isolation flags (`-ffreestanding -nostdlib`). Employs `objcopy` to isolate memory spaces:
* `-j .text` isolates the instruction stream to produce `imem.bin`.
* `-R .text` masks out the instruction stream to pack all data structures into `dmem.bin`.



### 📝 Manifest Generation (`benches.lst`)

Upon a validated build cycle, the compiler utilities emit a standardized test manifest (`benches.lst`) within the respective target deployment folders:

```text
<test_identifier>,<relative_path_to_imem>,<relative_path_to_dmem>

```

This structured record layout is parsed natively by test benches (`pytest`) to dynamically parameterize execution targets.

---

## 🚀 Execution

To trigger an isolated rebuild of the entire validation framework, run the master orchestration script from the execution context:

```bash
python build.py

```

The script automatically flushes obsolete artifact directories inside `build/`, executes the compilation routines sequentially, handles error diagnostics via terminal feedback loops, and exports the structural verification manifests.


# 🧪 RISC-V Tests & Benchmarks

This directory contains the testing framework for both the Single-Cycle and Pipelined RISC-V models. It includes a built-in system to compile Assembly and C tests into RISC-V binaries and run them through `pytest`.

---

## 🚀 How to Run Tests

We use `pytest` to run tests and compare the CPU output against the expected results.

```bash
# Run all tests (Single-Cycle and Pipeline)
pytest tests/cpu

# Run only Single-Cycle tests
pytest tests/cpu/test_SC.py

# Run only Pipeline tests
pytest tests/cpu/test_PL.py

# Run only fast tests (skip long benchmarks)
pytest tests/cpu --max-duration-scale=2

```

### ⏱️ Filtering Options

* `--max-duration-scale` (default: `5`): Filters tests by their duration rating (scale from 1 to 5). Any test with a `duration_scale` higher than this limit will be automatically skipped.



---

### 📊 Tracing & Reports

When you run tests, the system automatically generates helpful files for debugging and performance analysis:

* **Performance Reports:** Found in `tests/cpu/reports/`. Shows cycle counts, instructions per cycle (CPI), stalls, and jumps.
* **VCD Waveforms:** Generates `.vcd` files to view signals in GTKWave.
* **CSV Data Tracers:** Logs cycle-by-cycle register values, pipeline stages, and executed instructions.
from pathlib import Path
from enum import Enum


# ============================================================
# TEST PARAMETERS
# ============================================================

# Testbench limits
TIMEOUT_ITERATIONS = 20000
RF_DBG_NUM = 31  # Signature register (x31)

# ============================================================
# TRACING PARAMETERS
# ============================================================

# Waveform / CSV dump settings
BASE_TRACE_ENABLE = True
CVD_TRACE_ENABLE = False

TRACE_DIRNAME = Path("trace")
VCD_CLOCK_PERIOD_NS = 10

SC_TRACE_DIR = TRACE_DIRNAME / "sc"
PL_TRACE_DIR = TRACE_DIRNAME / "pl"

FULL_PERF_REPORT_COLS = ["cycles", "instructions", "cpi",
                         "stalls", "flushes", "jumps", "jpi", "status"]

COMPACT_PERF_REPORT_COLS = ["cycles", "cpi"]

PERF_SUMMARY_NAME = "performance_summary.csv"

# ============================================================
# HARDWARE CONFIGURATION
# ============================================================

XLEN = 32
REG_COUNT = 32

# ============================================================
# CPU STATUS
# ============================================================


class CpuTestResult(Enum):
    TEST_RUN = 0
    TEST_PASS = 1
    TEST_FAIL = 2

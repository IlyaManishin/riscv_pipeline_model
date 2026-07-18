from pathlib import Path


from enum import Enum


# ============================================================
# TEST PARAMETERS
# ============================================================

# Testbench limits
TIMEOUT_ITERATIONS = 20000
RF_DBG_NUM = 31  # Signature register (x31)

# Waveform / CSV dump settings
TRACE_ENABLE = True
TRACE_DIRNAME = Path("trace")
VCD_CLOCK_PERIOD_NS = 10

SC_TRACE_DIR = TRACE_DIRNAME / "sc"
PL_TRACE_DIR = TRACE_DIRNAME / "pl"


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

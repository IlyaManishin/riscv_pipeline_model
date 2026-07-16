import os
from enum import Enum


# ============================================================
# HARDWARE CONFIGURATION
# ============================================================

XLEN = 32
REG_COUNT = 32

# Testbench limits
TIMEOUT_ITERATIONS = 10000
RF_DBG_NUM = 31  # Signature register (x31)

# Waveform / CSV dump settings
TRACE_ENABLE = True
TRACE_DIRNAME = "trace"
VCD_TRACE_ENABLE = os.getenv("VCD_TRACE_ENABLE", "1").strip().lower() not in {
    "0", "false", "no", "off",
}
VCD_CLOCK_PERIOD_NS = 10


# ============================================================
# CPU STATUS
# ============================================================

class CpuTestResult(Enum):
    TEST_RUN = 0
    TEST_PASS = 1
    TEST_FAIL = 2

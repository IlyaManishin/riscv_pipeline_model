from enum import Enum

# ============================================================
# HARDWARE CONFIGURATION
# ============================================================

XLEN = 32
REG_COUNT = 32

# Testbench limits
TIMEOUT_ITERATIONS = 50000
RF_DBG_NUM = 31  # Signature register (x31)

# Waveform / CSV dump settings
TRACE_ENABLE = True
TRACE_DIRNAME = "trace"


# ============================================================
# CPU STATUS
# ============================================================

class CpuTestResult(Enum):
    TEST_RUN = 0
    TEST_PASS = 1
    TEST_FAIL = 2
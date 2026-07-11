from enum import Enum
from pathlib import Path

XLEN = 32
TIMEOUT_ITERATIONS = 50000
RF_DBG_NUM = 31

TRACE_ENABLE = True
TRACE_DIRNAME = "trace"


class CpuTestResult(Enum):
    TEST_RUN = 0
    TEST_PASS = 1
    TEST_FAIL = 2

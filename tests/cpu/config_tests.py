from enum import Enum
from pathlib import Path

TIMEOUT_ITERATIONS = 50000
RF_DBG_NUM = 31

TEST_DIR = Path(__file__).resolve().parent / "uBench" / "hex"


TRACE_ENABLE = True
TRACE_DIR = "trace"


class Test_Result(Enum):
    TEST_RUN = 0
    TEST_PASS = 1
    TEST_FAIL = 2

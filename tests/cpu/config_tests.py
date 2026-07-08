from enum import Enum


TIMEOUT_ITERATIONS = 50000
RF_DBG_NUM = 31

TEST_DIR = "C:\\Users\\Lecoo\\Documents\\rv-nsu\\prg\\uBench\\hex"


TRACE_ENABLE = True
TRACE_DIR = "trace"

class Test_Result(Enum):
    TEST_RUN = 0
    TEST_PASS = 1
    TEST_FAIL = 2
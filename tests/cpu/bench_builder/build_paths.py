from pathlib import Path

BENCHES_DIR = Path(__file__).resolve().parent / "sources"
BUILD_DIR = BENCHES_DIR / "build"

ASM_DIRNAME = "asm"
C_DIRNAME = "C"
TEST_LIST_NAME = "benches.lst"
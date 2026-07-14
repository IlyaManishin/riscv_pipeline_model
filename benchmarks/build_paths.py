from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BENCHES_DIR = ROOT_DIR / "sources"
BUILD_DIR = ROOT_DIR / "build"

ASM_DIRNAME = "asm"
C_DIRNAME = "C"
TEST_LIST_NAME = "benches.lst"
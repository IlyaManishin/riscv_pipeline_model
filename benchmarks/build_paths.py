from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BENCHES_DIR = ROOT_DIR / "sources"
BUILD_DIR = ROOT_DIR / "build"

ASM_DIRNAME = "asm"
C_DIRNAME = "C"
TEST_LIST_NAME = "benches.lst"

C_BUILD_DIR = BUILD_DIR / C_DIRNAME
ASM_BUILD_DIR = BUILD_DIR / ASM_DIRNAME

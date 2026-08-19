from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

# sources and build paths  
BENCHES_DIR = ROOT_DIR / "sources"
BUILD_DIR = ROOT_DIR / "build"

TEST_LIST_NAME = "benches.lst"
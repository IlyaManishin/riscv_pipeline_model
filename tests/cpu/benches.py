from runner import collect_tests
from benchmarks.build_paths import BUILD_DIR, ASM_DIRNAME, C_DIRNAME

# ============================================================
# TEST SUITE PREPARATION
# ============================================================

ASM_TESTS = collect_tests(BUILD_DIR / ASM_DIRNAME)
ASM_IDS = [test_item[0] for test_item in ASM_TESTS]

C_TESTS = collect_tests(BUILD_DIR / C_DIRNAME)
C_IDS = [test_item[0] for test_item in C_TESTS]

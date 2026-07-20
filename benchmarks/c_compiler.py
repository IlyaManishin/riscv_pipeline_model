import os
import sys
import subprocess
import shutil
from pathlib import Path
from tqdm import tqdm
import shutil

import build_paths as bpaths
from riscv_linker import riscv_compiler
# ============================================================
# CONFIGURATION
# ============================================================

# Input directory containing C source files
IN_DIR = bpaths.BENCHES_DIR / bpaths.C_DIRNAME

# Base output directory for compiled C tests
OUT_DIR = bpaths.BUILD_DIR / bpaths.C_DIRNAME

# Path to the directory containing the Makefile (relative to this script)
MAKEFILE_DIR = Path("riscv_linker")

# Path to the list file containing successfully compiled test binaries
LST_PATH = OUT_DIR / bpaths.TEST_LIST_NAME

# Keywords to exclude from the final list file
LST_UNUSED = ['Deprecated']

# ============================================================
# FUNCTIONS
# ============================================================


def find_c_files(directory: Path):
    """Recursively find all .c files in the specified directory."""
    return [
        f for f in directory.rglob("*")
        if f.suffix.lower() == ".c"
    ]


def compile_c_file(c_file: Path, makefile_dir: Path, final_out_dir: Path) -> dict:
    errors = []
    warnings = []
    dumps = {}

    # Compile with python subprocess
    success = riscv_compiler.compile_riscv(src_file=c_file, target_dir=final_out_dir)

    if not success:
        errors.append(f"Embedded compiler failed for {c_file.name}")
        return {"success": False, "errors": errors, "warnings": warnings, "dumps": dumps}

    final_imem = final_out_dir / "imem.bin"
    final_dmem = final_out_dir / "dmem.bin"

    if not final_imem.exists():
        errors.append(
            f"Compilation reported success, but {final_imem} is missing")
        return {"success": False, "errors": errors, "warnings": warnings, "dumps": dumps}

    try:
        dumps["imem"] = str(final_imem.relative_to(OUT_DIR))
        if final_dmem.exists():
            dumps["dmem"] = str(final_dmem.relative_to(OUT_DIR))
    except ValueError:
        dumps["imem"] = str(final_imem)

    return {"success": True, "errors": errors, "warnings": warnings, "dumps": dumps}


def main():
    """Main entry point for the C test compilation script."""
    # Validate input directory exists
    if not IN_DIR.exists():
        print(f"Error: input directory '{IN_DIR}' not found!")
        sys.exit(1)

    # Validate Makefile exists
    if not (MAKEFILE_DIR / "Makefile").exists():
        print(f"Error: Makefile not found at '{MAKEFILE_DIR / 'Makefile'}'")
        sys.exit(1)

    processed_files = []

    # Clear OUT_DIR
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
        print(f"REMOVE {OUT_DIR} directory")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Discover all C files to compile
    c_files = find_c_files(IN_DIR)

    if not c_files:
        print(f"No .c files found in {IN_DIR}")
        sys.exit(0)

    # Counters for final summary
    success_count = 0
    fail_count = 0

    # Terminal color codes for pretty console output
    GREEN = '\033[32m'
    RED = '\033[91m'
    RESET = '\033[0m'
    YELLOW = '\033[33m'
    COLOR_PATH = '\033[96m'

    # Process each C file individually
    for c_file in tqdm(c_files, desc="Compiling C", unit="file"):
        # Determine the relative path to preserve directory structure
        rel_path = c_file.relative_to(IN_DIR)

        # Create a specific output subdirectory for this test
        if rel_path.parent == Path('.'):
            out_subdir = OUT_DIR / c_file.stem
        else:
            out_subdir = OUT_DIR / rel_path.parent / c_file.stem

        # Run the compilation process
        result = compile_c_file(c_file, MAKEFILE_DIR, out_subdir)

        if result["success"]:
            success_count += 1

            name = c_file.stem

            # Extract both paths
            imem_path = result["dumps"].get("imem")
            dmem_path = result["dumps"].get("dmem")

            # Fallback if dmem wasn't recorded but exists in the output dir
            if not dmem_path:
                dmem_path = str((out_subdir / "dmem.bin").relative_to(OUT_DIR))

            # Format as "name, imem_path, dmem_path" and add to list
            processed_files.append(f"{name},{imem_path},{dmem_path}")
        else:
            fail_count += 1
            tqdm.write(f"  {COLOR_PATH}{rel_path}{RESET}")
            for err in result["errors"]:
                tqdm.write(f"    {RED}ERROR: {err}{RESET}")
            for warn in result["warnings"]:
                tqdm.write(f"    {YELLOW}WARNING: {warn}{RESET}")

    # Print final statistics
    print("=" * 50)
    print(
        f"Done! {GREEN}Success: {success_count}{RESET}, {RED}Failed: {fail_count}{RESET}")
    print(f"Output files saved to: {COLOR_PATH}{OUT_DIR}{RESET}")

    # Generate the list file containing both imem and dmem paths
    if LST_PATH is not None:
        with open(LST_PATH, "w", encoding="utf-8") as f:
            for item in processed_files:
                # Skip items that match any of the unused keywords
                if item and all([unus not in item for unus in LST_UNUSED]):
                    f.write(item + "\n")

        print(f"Processed files list saved to: {COLOR_PATH}{LST_PATH}{RESET}")


if __name__ == "__main__":
    main()

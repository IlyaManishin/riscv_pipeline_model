import subprocess
import sys
import shutil
from pathlib import Path

import build_paths as bpaths

# Master build script to orchestrate ASM and C test compilation

# List of builder scripts to run sequentially
BUILD_SCRIPTS = [
    "c_compiler.py",
    "RARS_compiler.py"
]


def main():
    print("=" * 50)
    print("STARTING FULL TESTS BUILD")
    print("=" * 50)

    # Clean the build directory before starting
    if bpaths.BUILD_DIR.exists():
        print(f"\n>>> Cleaning build directory: {bpaths.BUILD_DIR} <<<")
        shutil.rmtree(bpaths.BUILD_DIR)
        print("Cleaned successfully.")

    for script_name in BUILD_SCRIPTS:
        script_path = Path(__file__).parent / script_name

        if not script_path.exists():
            print(f"\n[ERROR] Build script not found: {script_name}")
            sys.exit(1)

        print(f"\n>>> Running: {script_name} <<<")

        # CRITICAL: Use sys.executable to ensure it runs in the SAME Python venv
        result = subprocess.run(
            [sys.executable, str(script_path)],
            # Ensure scripts run in their own directory context
            cwd=str(script_path.parent)
        )

        if result.returncode != 0:
            print(
                f"\n[FAILED] {script_name} exited with code {result.returncode}")
            sys.exit(1)

    print("\n" + "=" * 50)
    print("ALL BUILDS SUCCESSFUL")
    print("=" * 50)


if __name__ == "__main__":
    main()

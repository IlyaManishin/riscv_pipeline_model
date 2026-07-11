#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

from . import build_paths as bpaths

# ============================================================
# CONFIGURATION
# ============================================================

# Input directory with source files (.s, .asm)
IN_DIR = bpaths.BENCHES_DIR / bpaths.ASM_DIRNAME

# Output directory for .hex files
OUT_DIR = bpaths.BUILD_DIR / bpaths.ASM_DIRNAME

# Path to RARS (either .jar file or executable)
RARS_PATH = Path("rars1_6.jar")

# Path to lst file (list .hex files)
# if = None, lst file not create
LST_PATH = OUT_DIR / "ub.lst"
# LST_PATH = Path("./uBench/hex/ub.lst")
LST_UNUSED = ['Deprecated']

DUMP_CONFIG = {
    # Segment name from RARS (the memory region to dump)
    '.text': {
        # Format of the output file:
        # - 'HexText': ASCII hex representation, one 32-bit word per line
        # - 'Binary': Raw binary data (useful for direct memory loading)
        # - 'Text': Human-readable disassembly (not recommended for machine processing)
        'format': 'HexText',

        # Output file path template with placeholders
        # Available placeholders:
        #   %name%     - test name without extension (e.g., 'add_test_01')
        #   %fullname% - full filename (e.g., 'add_test_01.s')
        #   %parent%   - parent directory name
        #   %segment%  - segment name without dot (e.g., 'text', 'data')
        #   %date%     - current date (YYYY-MM-DD)
        #   %time%     - current time (HH-MM-SS)
        #   %year%     - current year (YYYY)
        #   %month%    - current month (MM)
        #   %day%      - current day (DD)
        #
        # Examples:
        #   './%name%_imem.hex'           -> hex_out/add_test_01_imem.hex
        #   './%name%/%name%_imem.hex'    -> hex_out/add_test_01/add_test_01_imem.hex
        #   './%segment%/%name%.hex'      -> hex_out/text/add_test_01.hex
        #   './%date%/%name%_imem.hex'    -> hex_out/2024-01-15/add_test_01_imem.hex
        #   '../%name%_imem.hex'          -> ../add_test_01_imem.hex (outside output_dir)
        #   'C:/tests/%name%_imem.hex'    -> absolute path
        'output_file_path': './%name%.hex'
    },
}

# imem and dmem config
"""
DUMP_CONFIG = {
    '.text': {
        'format': 'HexText',
        'output_file_path': './%name%/%name%.imem'
    },
    '.data': {
        'format': 'HexText',
        'output_file_path': './%name%/%name%.dmem'
    }
}
"""

# ============================================================
# FUNCTIONS
# ============================================================


def find_asm_files(directory: Path):
    return [
        f for f in directory.rglob("*")
        if f.suffix.lower() in [".s", ".asm"]
    ]


def convert_to_hex(asm_file: Path, dump_config: dict, output_dir: Path) -> dict:
    """Run RARS to convert .s/.asm file to multiple hex dumps based on config

    Args:
        asm_file: Path to assembly file
        dump_config: Dictionary where keys are segment names (e.g., '.text', '.data')
                     and values are dicts with keys:
                         - 'format': 'HexText', 'Binary', or 'Text'
                         - 'output_file_path': path template with placeholders
                           Available placeholders:
                               %name% - test name without extension (e.g., 'add_test_01')
                               %fullname% - full filename (e.g., 'add_test_01.s')
                               %parent% - parent directory name
                               %segment% - segment name (e.g., '.text', '.data')
                               %date% - current date (YYYY-MM-DD)
                               %time% - current time (HH-MM-SS)

                           Examples:
                               './%name%_imem.hex' -> saves in output_dir as 'add_test_01_imem.hex'
                               './%name%/%segment%_dump.bin' -> creates subfolder with test name
                               './subdir/%name%_data.bin' -> nested subdirectories
                               '../external/%name%/code.hex' -> relative path outside output_dir
                               'C:/absolute/path/%name%.bin' -> absolute path

    Returns:
        bool: True if all dumps succeeded, False otherwise
    """

    errors = []
    warnings = []
    dumps = {}

    hex_files = {}

    for segment, config in dump_config.items():
        path_template = config.get(
            'output_file_path', f'./%name%{config.get("add_in_name", "")}{config.get("extension", "")}')

        current_time = datetime.now()
        replacements = {
            '%name%': asm_file.stem,
            '%fullname%': asm_file.name,
            '%parent%': asm_file.parent.name,
            '%segment%': segment.lstrip('.'),  # убираем точку в начале
            '%date%': current_time.strftime('%Y-%m-%d'),
            '%time%': current_time.strftime('%H-%M-%S'),
            '%year%': current_time.strftime('%Y'),
            '%month%': current_time.strftime('%m'),
            '%day%': current_time.strftime('%d'),
        }

        expanded_path = path_template
        for placeholder, value in replacements.items():
            expanded_path = expanded_path.replace(placeholder, value)

        if os.path.isabs(expanded_path):
            output_file = Path(expanded_path)
        else:
            output_file = output_dir / expanded_path

        output_file.parent.mkdir(parents=True, exist_ok=True)

        hex_files[segment] = output_file
    for segment, output_file in hex_files.items():
        try:
            rel_path = output_file.relative_to(output_dir)
        except ValueError:
            rel_path = output_file
        dumps[segment] = str(rel_path)

    if str(RARS_PATH).endswith(".jar"):
        cmd_base = ["java", "-jar", str(RARS_PATH), "a", "nc", str(asm_file)]
    else:
        cmd_base = [str(RARS_PATH), "a", "nc", str(asm_file)]

    dump_args = []
    for segment, output_file in hex_files.items():
        fmt = dump_config[segment]['format']
        dump_args.extend(["dump", segment, fmt, str(output_file)])

    cmd = cmd_base + dump_args

    try:
        result = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            text=True
        )

        combined_output = result.stdout + result.stderr
        if result.stdout != '':
            for line in combined_output.split('\n'):
                if line != '':
                    errors.append(line.strip())

            for output_file in hex_files.values():
                if output_file.exists() and output_file.stat().st_size == 0:
                    output_file.unlink()

            return {
                "success": False,
                "errors": errors,
                "warnings": warnings,
                "dumps": dumps
            }

        all_valid = True
        for segment, output_file in hex_files.items():
            if not output_file.exists():
                errors.append(
                    f"{segment} dump file was not created: {output_file}")
                all_valid = False
            elif output_file.stat().st_size == 0:
                warnings.append(f"{segment} dump file is empty: {output_file}")

        return {
            "success": all_valid,
            "errors": errors,
            "warnings": warnings,
            "dumps": dumps
        }

    except subprocess.TimeoutExpired:
        errors.append(f"TIMEOUT processing {asm_file.name}")
        return {"success": False, "errors": errors, "warnings": warnings, "dumps": dumps}

    except FileNotFoundError:
        errors.append(f"RARS not found at: {RARS_PATH}")
        errors.append("Check RARS_PATH configuration")
        return {"success": False, "errors": errors, "warnings": warnings, "dumps": dumps}

    except Exception as e:
        errors.append(str(e))
        return {"success": False, "errors": errors, "warnings": warnings, "dumps": dumps}


def main():
    if not IN_DIR.exists():
        print(f"Error: input directory '{IN_DIR}' not found!")
        sys.exit(1)

    processed_files = []

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    asm_files = find_asm_files(IN_DIR)

    if not asm_files:
        print(f"No .s or .asm files found in {IN_DIR}")
        sys.exit(0)

    print(f"Found {len(asm_files)} files to convert")
    print("=" * 50)

    success_count = 0
    fail_count = 0

    GREEN = '\033[32m'
    RED = '\033[91m'
    RESET = '\033[0m'
    YELLOW = '\033[33m'
    COLOR_PATH = '\033[96m'

    for asm_file in asm_files:
        rel_path = asm_file.relative_to(IN_DIR)

        if rel_path.parent == Path('.'):
            out_subdir = OUT_DIR
        else:
            out_subdir = OUT_DIR / rel_path.parent

        print(f"Converting: {COLOR_PATH}{rel_path}{RESET}:")

        result = convert_to_hex(asm_file, DUMP_CONFIG, out_subdir)

        if result["success"]:
            success_count += 1
            for res_file in result["dumps"].values():
                processed_files.append(
                    str((out_subdir / res_file).relative_to(OUT_DIR)))
            print(f"  {GREEN}OK{RESET}")
        else:
            fail_count += 1
            print(f"  {RED}FAILED{RESET}")

        for err in result["errors"]:
            print(f"  {RED}ERROR: {err}{RESET}")

        for warn in result["warnings"]:
            print(f"  {YELLOW}WARNING: {warn}{RESET}")

    print("=" * 50)
    print(
        f"Done! {GREEN}Success: {success_count}{RESET}, {RED}Failed: {fail_count}{RESET}")
    print(f"Output files saved to: {COLOR_PATH}{OUT_DIR}{RESET}")

    if LST_PATH is not None:
        with open(LST_PATH, "w", encoding="utf-8") as f:
            for item in processed_files:
                if all([unus not in item for unus in LST_UNUSED]):
                    f.write(item + "\n")

        print(f"Processed files list saved to: {COLOR_PATH}{LST_PATH}{RESET}")


if __name__ == "__main__":
    main()

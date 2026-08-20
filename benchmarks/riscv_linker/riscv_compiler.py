import subprocess
import shutil
from pathlib import Path

# ===============================================================
# CONFIGURATION
# ===============================================================

SCRIPT_DIR = Path(__file__).resolve().parent

#--------------------------PATHS-------------------------------
LINKER_DIR   = SCRIPT_DIR / "linker"
TEMPS_DIR    = SCRIPT_DIR / "temps"
RES_DIR      = SCRIPT_DIR / "result"

START_SCRIPT = LINKER_DIR / "start.s"
LINKER       = LINKER_DIR / "riscv.ld"

SRC          = ["test.c", "utils.c"]
OUT_NAME     = "res"

#--------------------------VARS-------------------------------
CC           = "riscv64-unknown-elf-gcc"
OBJCOPY      = "riscv64-unknown-elf-objcopy"

DEFAULT_IMEM_SIZE  = 2**12
DEFAULT_DMEM_SIZE  = 2**12
DEFAULT_STACK_SIZE = 2**9

RISC32_FLAGS = ["-march=rv32i", "-mabi=ilp32", "-save-temps"]
COMPR_FLAGS  = [
    "-ffreestanding", "-nostdlib", "-ffunction-sections",
    "-fdata-sections", "-fno-asynchronous-unwind-tables", "-fno-unwind-tables"
]


# ===============================================================
# COMPILING
# ===============================================================

def compile_riscv(
    src_files: list[str | Path] | str | Path,
    target_dir: str | Path = RES_DIR,
    imem_size: int = DEFAULT_IMEM_SIZE,
    dmem_size: int = DEFAULT_DMEM_SIZE,
    stack_size: int = DEFAULT_STACK_SIZE
) -> bool:
    # normalize src_files into a list of absolute resolved Paths
    if isinstance(src_files, (str, Path)):
        src_list = [Path(src_files).resolve()]
    else:
        src_list = [Path(f).resolve() for f in src_files]

    res_dir = Path(target_dir)    

    out  = res_dir / OUT_NAME
    imem = res_dir / "imem.bin"
    dmem = res_dir / "dmem.bin"

    # dynamic linker arguments for memory configuration
    ldflags = [
        "-T", str(LINKER),
        "-Wl,--gc-sections",
        f"-Wl,--defsym,IMEM_SIZE={imem_size}",
        f"-Wl,--defsym,DMEM_SIZE={dmem_size}",
        f"-Wl,--defsym,STACK_SIZE={stack_size}"
    ]

    if res_dir.exists():
        for f in res_dir.glob("*"):
            if f.is_file(): 
                f.unlink()
    if TEMPS_DIR.exists():
        shutil.rmtree(TEMPS_DIR)

    #--------------------------BUILD--------------------------------
    res_dir.mkdir(parents=True, exist_ok=True)
    TEMPS_DIR.mkdir(parents=True, exist_ok=True)

    temp_out = TEMPS_DIR / OUT_NAME
    src_cmd_args = [str(f) for f in src_list]
    cc_cmd = [CC] + RISC32_FLAGS + COMPR_FLAGS + ldflags + src_cmd_args + [str(START_SCRIPT), "-o", str(temp_out)]
    
    res = subprocess.run(cc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Compilation Error:\n{res.stderr}")
        return False

    shutil.move(str(temp_out), str(out))

    # only .text section
    try:
        subprocess.run([OBJCOPY, "-O", "binary", "-j", ".text", str(out), str(imem)], check=True)
    except Exception as e:
        print(f"Objcopy imem Error: {e}")
        return False

    # all sections except .text
    try:
        subprocess.run([OBJCOPY, "-O", "binary", "-R", ".text", str(out), str(dmem)], check=True)
    except subprocess.CalledProcessError:
        pass

    TEMPS_DIR.joinpath("i_files").mkdir(parents=True, exist_ok=True)
    TEMPS_DIR.joinpath("o_files").mkdir(parents=True, exist_ok=True)
    TEMPS_DIR.joinpath("s_files").mkdir(parents=True, exist_ok=True)
    
    for f in TEMPS_DIR.glob("*.i"): 
        shutil.move(str(f), str(TEMPS_DIR / "i_files" / f.name))
    for f in TEMPS_DIR.glob("*.o"): 
        shutil.move(str(f), str(TEMPS_DIR / "o_files" / f.name))
    for f in TEMPS_DIR.glob("*.s"): 
        shutil.move(str(f), str(TEMPS_DIR / "s_files" / f.name))

    final_elf = res_dir / "res.bin"
    if out.exists():
        shutil.move(str(out), str(final_elf))

    return True


if __name__ == "__main__":
    print(f"Running standalone build for: {SRC}")
    compile_riscv(SRC)
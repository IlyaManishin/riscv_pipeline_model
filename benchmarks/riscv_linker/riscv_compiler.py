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

SRC          = "test.c"
OUT_NAME     = "res"

#--------------------------VARS-------------------------------
CC           = "riscv64-unknown-elf-gcc"
OBJCOPY      = "riscv64-unknown-elf-objcopy"

RISC32_FLAGS = ["-march=rv32i", "-mabi=ilp32", "-save-temps"]
COMPR_FLAGS  = [
    "-ffreestanding", "-nostdlib", "-ffunction-sections",
    "-fdata-sections", "-fno-asynchronous-unwind-tables", "-fno-unwind-tables"
]
LDFLAGS      = ["-T", str(LINKER), "-Wl,--gc-sections"]


# ===============================================================
# COMPILING
# ===============================================================

def compile_riscv(src_file: str | Path, target_dir: str | Path = RES_DIR) -> bool:
    src = Path(src_file).resolve()
    res_dir = Path(target_dir)    

    out  = res_dir / OUT_NAME
    imem = res_dir / "imem.bin"
    dmem = res_dir / "dmem.bin"

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
    cc_cmd = [CC] + RISC32_FLAGS + COMPR_FLAGS + LDFLAGS + [str(src), str(START_SCRIPT), "-o", str(temp_out)]
    
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
#--------------------------PATHS-------------------------------
LINKER_DIR   = linker
TEMPS_DIR    = temps
RES_DIR      = result

START_SCRIPT = $(LINKER_DIR)/start.s
LINKER       = $(LINKER_DIR)/riscv.ld

SRC         ?= test.c
OUT_NAME     = res

OUT          = $(RES_DIR)/$(OUT_NAME)  
IMEM         = $(RES_DIR)/imem.bin  
DMEM         = $(RES_DIR)/dmem.bin


#--------------------------CONFIG-------------------------------
CC           = riscv64-unknown-elf-gcc
OBJCOPY      = riscv64-unknown-elf-objcopy

RISC32_FLAGS = -march=rv32i -mabi=ilp32 -save-temps
COMPR_FLAGS  = -ffreestanding -nostdlib -ffunction-sections \
               -fdata-sections -fno-asynchronous-unwind-tables -fno-unwind-tables
LDFLAGS      = -T $(LINKER) -Wl,--gc-sections


#--------------------------BUILD--------------------------------
all: $(IMEM) $(DMEM) move_temps

# only .text section
$(IMEM): $(OUT)
	$(OBJCOPY) -O binary -j .text $(OUT) $(IMEM) 

# all sections except .text
$(DMEM): $(OUT)
	$(OBJCOPY) -O binary -R .text $(OUT) $(DMEM)

$(OUT): $(SRC) $(LINKER) $(START_SCRIPT)
	mkdir -p $(RES_DIR)
	mkdir -p $(TEMPS_DIR)

	$(CC) $(RISC32_FLAGS) $(COMPR_FLAGS) $(LDFLAGS) $(SRC) $(START_SCRIPT) -o $(TEMPS_DIR)/$(OUT_NAME)
	mv $(TEMPS_DIR)/$(OUT_NAME) $(OUT)

clean:
	rm $(RES_DIR)/*
	rm -rf $(TEMPS_DIR)/

move_temps:
	mkdir -p $(TEMPS_DIR)/i_files $(TEMPS_DIR)/o_files $(TEMPS_DIR)/s_files
	mv $(TEMPS_DIR)/*.i $(TEMPS_DIR)/i_files 2>/dev/null || true
	mv $(TEMPS_DIR)/*.o $(TEMPS_DIR)/o_files 2>/dev/null || true
	mv $(TEMPS_DIR)/*.s $(TEMPS_DIR)/s_files 2>/dev/null || true

.PHONY: all clean
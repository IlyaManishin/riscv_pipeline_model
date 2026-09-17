from pathlib import Path
from typing import Any

from risc_v.base.icpu_system import ICpuSystem
from risc_v.riscv_config import Instruction, IMEM_ADDR_BYTE_WIDTH
from models.pipeline.cpu_system import CpuSystem as PL_CpuSystem

from tests.cpu.tests_config import REG_COUNT
from .base_tracers import CsvTracer

# ============================================================
# COMMON_REGISTER_MONITOR_TRACER
# ============================================================


class RegisterTracer(CsvTracer):
    def __init__(self, cpu: ICpuSystem, trace_dir: str | Path, tracer_name: str = "reg"):
        super().__init__(trace_dir, tracer_name)
        self.cpu = cpu

    def get_header(self) -> list[str]:
        header = ["cycle", "pc"]
        header.extend(f"x{i}" for i in range(REG_COUNT))
        return header

    def trace_cycle(self, cycle: int) -> None:
        if self.writer is None or self.cpu is None:
            return
        row = [
            cycle,
            self.cpu.get_cur_pc()
        ]
        for i in range(REG_COUNT):
            row.append(self.cpu.reg_file.read(i))
        self.write_row(row)


# ============================================================
# PIPELINE ARCHITECTURE TRACER
# ============================================================

def uint32_to_int32(value: int) -> int:
    return value if value < 0x80000000 else value - 0x100000000


class PipelineTracer(CsvTracer):
    def __init__(self, cpu: PL_CpuSystem | Any, trace_dir: str | Path, tracer_name: str = "pipeline"):
        super().__init__(trace_dir, tracer_name)
        self.cpu = cpu

    def get_header(self) -> list[str]:
        header = ["cycle",
                  "pc_next", "is_jump",
                  "jfexe_M",
                  "alu_out",
                  "rf_we3", "rd", "rf_wd3",
                  "is_stall",
                  "fetch instr", "decoder instr", "execute instr",
                  "memory instr", "dmemsel",
                  "wb instr"]
        header.extend(f"x{i}" for i in range(REG_COUNT))
        return header

    def trace_cycle(self, cycle: int) -> None:
        if self.writer is None:
            return

        core = self.cpu.core
        wb_stage = core.stage_writeback
        hdu = core.hdu

        is_jump = hdu.jfexe_hazard

        row = [
            cycle,
            self.cpu.get_cur_pc(),
            is_jump,
            core.jfexe_M.read(),
            uint32_to_int32(core.stage_execute.alu_out),
            wb_stage.rf_we3,
            wb_stage.rd,
            wb_stage.rf_wd3,
            hdu.raw_hazard,
            self.disasm_pc_instr(core.stage_fetch.pc_next,
                                 core.stage_fetch.valid),
            self.disasm_instr(core.stage_decode.instr,
                              core.stage_decode.valid),
            self.disasm_instr(core.buff_id_ex.instr.read(),
                              core.stage_execute.valid),
            self.disasm_instr(core.buff_ex_mem.instr.read(),
                              core.stage_memory.valid),
            bin(core.stage_memory.dmem_funct3),
            self.disasm_instr(core.buff_mem_wb.instr.read(),
                              core.stage_writeback.valid)
        ]
        for i in range(REG_COUNT):
            row.append(self.cpu.reg_file.read(i))
        self.writer.writerow(row)

    def disasm_pc_instr(self, pc: int, valid: int | bool = True) -> str:
        if not bool(valid):
            return "nop"
        pc_mask = (1 << IMEM_ADDR_BYTE_WIDTH) - 1
        instr_raw = self.cpu.imem._memory[(pc & pc_mask) >> 2]
        return Instruction(instr_raw).disasm()

    def disasm_instr(self, instr: Instruction, valid: int | bool = True) -> str:
        if not bool(valid):
            return "nop"
        return instr.disasm()
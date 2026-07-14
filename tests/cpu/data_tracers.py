from cpu_config import REG_COUNT
from risc_v.base.icpu_system import ICpuSystem
from risc_v.pipeline.cpu_system import CpuSystem as PL_CpuSystem

from tracers import CsvTracer
from tests.utils import disasm

# ============================================================
# COMMON_REGISTER_MONITOR_TRACER
# ============================================================


class RegisterTracer(CsvTracer):
    def __init__(self, cpu: ICpuSystem = None, tracer_name: str = "register_trace"):
        super().__init__(tracer_name)
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
    def __init__(self, cpu: PL_CpuSystem, test_name):
        super().__init__(test_name)
        self.cpu = cpu

    def get_header(self) -> list[str]:
        header = ["cycle",
                  "pc", "stall_pc",
                  "jfexe", "jfid",
                  "alures", "imm_pc",
                  "disasm fetch", "disasm decoder", "disasm execute", "disasm memory", "disasm wb"]
        header.extend(f"x{i}" for i in range(REG_COUNT))
        return header

    def trace_cycle(self, cycle: int) -> None:
        if self.writer is None:
            return

        row = [
            cycle,
            self.cpu.get_cur_pc(),
            self.cpu.stage_fetch.stall_pc,
            self.cpu.stage_execute.jfexe,
            self.cpu.stage_decode.jfid,
            uint32_to_int32(self.cpu.stage_execute.alures),
            uint32_to_int32(self.cpu.stage_decode.imm_pc),
            self.disasm_stage(
                self.cpu.stage_fetch.pc_instr.read(), self.cpu.stage_fetch.valid),
            self.disasm_stage(self.cpu.stage_decode.pc,
                              self.cpu.stage_decode.valid),
            self.disasm_stage(self.cpu.stage_execute.pc4 - 4,
                              self.cpu.stage_execute.valid),
            self.disasm_stage(self.cpu.stage_memory.pc4 - 4,
                              self.cpu.stage_memory.valid),
            self.disasm_stage(self.cpu.stage_writeback.pc4 - 4,
                              self.cpu.stage_writeback.valid)

        ]
        for i in range(REG_COUNT):
            row.append(self.cpu.reg_file.read(i))

        self.writer.writerow(row)

    def disasm_stage(self, pc: int, valid: int):
        if not bool(valid):
            return "nop"
        instr = self.cpu.imem._memory[pc >> 2]
        dis_instr = disasm.disasm(instr)
        # return ("!" + dis_instr if not bool(valid) else dis_instr)
        return dis_instr

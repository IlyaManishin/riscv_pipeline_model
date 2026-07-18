"""VCD tracer integrated with the architectural test runner."""

from pathlib import Path
from typing import Any, TextIO

from tests.cpu.tests_config import REG_COUNT, TRACE_DIRNAME, XLEN
from risc_v.base.icpu_system import ICpuSystem
from .base_tracers import BaseTracer
from vcd import VCDWriter
from vcd.writer import Variable


class CpuVcdTracer(BaseTracer):
    """Record either CPU implementation through the normal tracer lifecycle."""

    def __init__(
        self,
        cpu: ICpuSystem,
        trace_dir: str | Path,
        tracer_name: str = "vcd",
        *,
        clock_period_ns: int = 10,
    ) -> None:
        super().__init__(trace_dir, tracer_name)
        if clock_period_ns < 2:
            raise ValueError("clock_period_ns must be at least 2")

        self.cpu = cpu
        self.clock_period_ns = clock_period_ns
        self.half_period_ns = clock_period_ns // 2
        self.writer: VCDWriter | None = None
        self.stream: TextIO | None = None
        self.signals: dict[str, Variable] = {}
        self.widths: dict[str, int] = {}
        self.output: Path | None = None
        self._pipeline = hasattr(cpu, "stage_fetch")

    def on_test_start(self, test_name: str) -> None:
        trace_dir = Path(self.trace_dir) / test_name
        self.output = (trace_dir / f"{self.tracer_name}.vcd").resolve()
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.output.open("w", encoding="utf-8", newline="\n")
        self.writer = VCDWriter(
            self.stream,
            timescale="1 ns",
            version="riscv_pipeline_model pytest tracer",
        )

        self._define_common_signals()
        if self._pipeline:
            self._define_pipeline_signals()
        else:
            self._define_single_cycle_signals()

        self._sample(timestamp=0, cycle=0)
        
    def _add(
        self,
        key: str,
        scope: tuple[str, ...],
        name: str,
        width: int = 1,
    ) -> None:
        if self.writer is None:
            raise RuntimeError("VCD writer has not been started")
        self.signals[key] = self.writer.register_var(
            scope,
            name,
            "wire",
            size=width,
            init=0,
        )
        self.widths[key] = width

    def _define_common_signals(self) -> None:
        self._add("clk", ("cpu",), "clk")
        self._add("cycle", ("cpu",), "cycle", 32)
        self._add("pc", ("cpu",), "pc", XLEN)
        for index in range(REG_COUNT):
            self._add(f"x{index}", ("cpu", "registers"), f"x{index}", XLEN)

    def _define_pipeline_signals(self) -> None:
        specs = {
            "if": (("valid", 1), ("pc", 32), ("instr", 32), ("stall", 1)),
            "id": (
                ("valid", 1), ("pc", 32), ("instr", 32),
                ("rs1", 5), ("rs2", 5), ("rd", 5),
                ("rf_rd1", 32), ("rf_rd2", 32), ("imm", 32),
                ("jump", 1), ("br_eq", 1), ("br_lt", 1),
            ),
            "ex": (
                ("valid", 1), ("pc", 32), ("instr", 32), ("rd", 5),
                ("alu_a", 32), ("alu_b", 32), ("alu_result", 32),
                ("shift_result", 32), ("jump", 1),
            ),
            "mem": (
                ("valid", 1), ("pc", 32), ("instr", 32), ("rd", 5),
                ("addr", 32), ("byte_we", 4), ("wdata", 32), ("rdata", 32),
            ),
            "wb": (
                ("valid", 1), ("pc", 32), ("instr", 32), ("rd", 5),
                ("reg_we", 1), ("reg_wdata", 32),
            ),
        }
        for stage, stage_specs in specs.items():
            for name, width in stage_specs:
                self._add(f"{stage}_{name}", ("cpu", "pipeline", stage), name, width)

    def _define_single_cycle_signals(self) -> None:
        specs = (
            ("instr", 32), ("rs1", 5), ("rs2", 5), ("rd", 5),
            ("rf_rd1", 32), ("rf_rd2", 32), ("imm", 32),
            ("alu_a", 32), ("alu_b", 32), ("alu_result", 32),
            ("shift_result", 32), ("dmem_addr", 32), ("dmem_byte_we", 4),
            ("dmem_wdata", 32), ("reg_we", 1), ("reg_wdata", 32),
        )
        for name, width in specs:
            self._add(f"sc_{name}", ("cpu", "single_cycle"), name, width)

    def _instr_at(self, pc: int, valid: int | bool = 1) -> int:
        if not valid:
            return 0
        memory: list[int] = getattr(self.cpu.imem, "_memory")
        addr_width = self.cpu.imem.get_addr_width()
        index = (int(pc) >> 2) & ((1 << addr_width) - 1)
        return memory[index]

    @staticmethod
    def _stage_pc(pc4: int, valid: int | bool) -> int:
        return ((int(pc4) - 4) & 0xFFFFFFFF) if valid else 0

    def _common_values(self, cycle: int) -> dict[str, int]:
        values = {"cycle": cycle, "pc": self.cpu.get_cur_pc()}
        values.update(
            {f"x{index}": self.cpu.reg_file.read(index) for index in range(REG_COUNT)}
        )
        return values

    def _pipeline_values(self) -> dict[str, int]:
        cpu: Any = self.cpu
        fetch = cpu.stage_fetch
        decode = cpu.stage_decode
        execute = cpu.stage_execute
        memory = cpu.stage_memory
        writeback = cpu.stage_writeback

        fetch_pc = int(fetch.pc)
        decode_pc = int(decode.pc) if decode.valid else 0
        execute_pc = self._stage_pc(execute.pc4, execute.valid)
        memory_pc = self._stage_pc(memory.pc4, memory.valid)
        writeback_pc = self._stage_pc(writeback.pc4, writeback.valid)

        return {
            "if_valid": fetch.valid,
            "if_pc": fetch_pc,
            "if_instr": self._instr_at(fetch_pc, fetch.valid),
            "if_stall": fetch.stall_pc,
            "id_valid": decode.valid,
            "id_pc": decode_pc,
            "id_instr": decode.instr.raw if decode.valid and decode.instr is not None else 0,
            "id_rs1": decode.rs1,
            "id_rs2": decode.rs2,
            "id_rd": decode.rd,
            "id_rf_rd1": decode.rf_rd1,
            "id_rf_rd2": decode.rf_rd2,
            "id_imm": decode.imm,
            "id_jump": decode.jfid,
            "id_br_eq": decode.br_eq,
            "id_br_lt": decode.br_lt,
            "ex_valid": execute.valid,
            "ex_pc": execute_pc,
            "ex_instr": self._instr_at(execute_pc, execute.valid),
            "ex_rd": execute.rd,
            "ex_alu_a": execute.alu_in_a,
            "ex_alu_b": execute.alu_in_b,
            "ex_alu_result": execute.alures,
            "ex_shift_result": execute.shres,
            "ex_jump": execute.jfexe,
            "mem_valid": memory.valid,
            "mem_pc": memory_pc,
            "mem_instr": self._instr_at(memory_pc, memory.valid),
            "mem_rd": memory.rd,
            "mem_addr": memory.dmem_addr,
            "mem_byte_we": memory.dmem_byte_we,
            "mem_wdata": memory.dmem_wdata,
            "mem_rdata": memory.dmem_rdata,
            "wb_valid": writeback.valid,
            "wb_pc": writeback_pc,
            "wb_instr": self._instr_at(writeback_pc, writeback.valid),
            "wb_rd": cpu.buff_mem_wb.rd.read(),
            "wb_reg_we": writeback.rf_we3,
            "wb_reg_wdata": writeback.rf_wd3,
        }

    def _single_cycle_values(self) -> dict[str, int]:
        core: Any = getattr(self.cpu, "_core")
        return {
            "sc_instr": core.instr.raw if core.instr is not None else 0,
            "sc_rs1": core.rs1,
            "sc_rs2": core.rs2,
            "sc_rd": core.rd,
            "sc_rf_rd1": core.rf_rd1,
            "sc_rf_rd2": core.rf_rd2,
            "sc_imm": core.imm,
            "sc_alu_a": core.alu_in_a,
            "sc_alu_b": core.alu_in_b,
            "sc_alu_result": core.alu_out,
            "sc_shift_result": core.shifter_out,
            "sc_dmem_addr": core.dmem_addr,
            "sc_dmem_byte_we": core.dmem_byte_we,
            "sc_dmem_wdata": core.dmem_wdata,
            "sc_reg_we": core.rf_we3,
            "sc_reg_wdata": core.rf_wd3,
        }

    def _change(self, key: str, timestamp: int, value: int | bool) -> None:
        if self.writer is None:
            return
        width = self.widths[key]
        masked = int(value) & ((1 << width) - 1)
        self.writer.change(self.signals[key], timestamp, masked)

    def _sample(self, timestamp: int, cycle: int) -> None:
        values = self._common_values(cycle)
        values.update(
            self._pipeline_values() if self._pipeline else self._single_cycle_values()
        )
        for key, value in values.items():
            self._change(key, timestamp, value)

    def trace_cycle(self, cycle: int) -> None:
        if self.writer is None:
            return

        rising_time = cycle * self.clock_period_ns + self.half_period_ns
        self._change("clk", rising_time, 1)
        self._sample(timestamp=rising_time, cycle=cycle + 1)

        self._change("clk", (cycle + 1) * self.clock_period_ns, 0)

    def on_test_end(self, test_name: str, passed: bool) -> None:
        self.close()

    def close(self) -> None:
        if self.writer is not None:
            try:
                self.writer.close()
            finally:
                self.writer = None
                if self.stream is not None:
                    self.stream.close()
                    self.stream = None

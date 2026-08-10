from sim_base.mem.register import Register
from sim_base.mem.block_mem import BlockMem


class IF_ID_Stage:
    pc: Register[int]
    instr: BlockMem
    valid: Register[bool]

    def __init__(self, imem: BlockMem):
        self.pc = Register(0)
        self.instr = imem  # imem is itself register-like (addr in -> data out next cycle)
        self.valid = Register(False)

    def get_registers(self) -> list[Register[int] | Register[bool]]:
        return [self.pc, self.valid]  # instr/imem is committed externally, not here

    def stall(self):
        for r in self.get_registers():
            r.set(r.read())

    def flush(self):
        self.pc.set(0)
        self.valid.set(False)


class ID_EX_Stage:
    pc: Register[int]
    rf_rd1: Register[int]
    rf_rd2: Register[int]
    imm: Register[int]
    rs1: Register[int]
    rs2: Register[int]
    rd: Register[int]
    alu_sel: Register[bool]
    shift_sel: Register[bool]
    a_sel: Register[bool]
    b_sel: Register[bool]
    wb_sel: Register[bool]
    reg_wr: Register[bool]
    dmem_sel: Register[bool]
    jfexe: Register[bool]
    alushift_sel: Register[bool]
    valid: Register[bool]

    def __init__(self):
        self.pc = Register(0)
        self.rf_rd1 = Register(0)
        self.rf_rd2 = Register(0)
        self.imm = Register(0)
        self.rs1 = Register(0)
        self.rs2 = Register(0)
        self.rd = Register(0)

        self.alu_sel = Register(False)
        self.shift_sel = Register(False)
        self.a_sel = Register(False)
        self.b_sel = Register(False)
        self.wb_sel = Register(False)
        self.reg_wr = Register(False)
        self.dmem_sel = Register(False)
        self.jfexe = Register(False)
        self.alushift_sel = Register(False)
        self.valid = Register(False)

    def get_registers(self) -> list[Register[int] | Register[bool]]:
        return [
            self.pc, self.rf_rd1, self.rf_rd2, self.imm,
            self.rs1, self.rs2, self.rd,
            self.alu_sel, self.a_sel, self.b_sel, self.wb_sel, self.reg_wr, self.dmem_sel,
            self.jfexe, self.alushift_sel, self.valid, self.shift_sel
        ]

    def stall(self):
        for r in self.get_registers():
            r.set(r.read())

    def flush(self):
        self.pc.set(0)
        self.rf_rd1.set(0)
        self.rf_rd2.set(0)
        self.imm.set(0)
        self.rs1.set(0)
        self.rs2.set(0)
        self.rd.set(0)
        self.alu_sel.set(False)
        self.shift_sel.set(False)
        self.a_sel.set(False)
        self.b_sel.set(False)
        self.wb_sel.set(False)
        self.reg_wr.set(False)
        self.dmem_sel.set(False)
        self.jfexe.set(False)
        self.alushift_sel.set(False)
        self.valid.set(False)


class EX_MEM_Stage:
    alu_out: Register[int]
    rf_rd2: Register[int]
    rd: Register[int]
    wb_sel: Register[bool]
    reg_wr: Register[bool]
    dmem_sel: Register[bool]
    pc4: Register[int]
    valid: Register[bool]

    def __init__(self):
        self.alu_out = Register(0)
        self.rf_rd2 = Register(0)
        self.rd = Register(0)
        self.wb_sel = Register(False)
        self.reg_wr = Register(False)
        self.dmem_sel = Register(False)
        self.pc4 = Register(0)
        self.valid = Register(False)

    def get_registers(self) -> list[Register[int] | Register[bool]]:
        return [
            self.alu_out, self.rf_rd2, self.rd,
            self.wb_sel, self.reg_wr, self.dmem_sel, self.pc4, self.valid
        ]

    def flush(self):
        self.alu_out.set(0)
        self.rf_rd2.set(0)
        self.rd.set(0)
        self.wb_sel.set(False)
        self.reg_wr.set(False)
        self.dmem_sel.set(False)
        self.pc4.set(0)
        self.valid.set(False)


class MEM_WB_Stage:
    alu_out: Register[int]
    dmem_data: BlockMem
    dmem_byte_off: Register[int]
    dmem_funct3: Register[int]
    rd: Register[int]
    wb_sel: Register[bool]
    reg_wr: Register[bool]
    pc4: Register[int]
    valid: Register[bool]

    def __init__(self, dmem: BlockMem):
        self.alu_out = Register(0)
        self.dmem_data = dmem  # dmem is itself register-like (addr in -> data out next cycle)
        self.dmem_byte_off = Register(0)
        self.dmem_funct3 = Register(0)
        self.rd = Register(0)
        self.wb_sel = Register(False)
        self.reg_wr = Register(False)
        self.pc4 = Register(0)
        self.valid = Register(False)

    def get_registers(self) -> list[Register[int] | Register[bool]]:
        return [
            self.alu_out, self.dmem_byte_off, self.dmem_funct3, self.rd,
            self.wb_sel, self.reg_wr, self.pc4, self.valid
        ]  # dmem_data/dmem is committed externally, not here

    def flush(self):
        self.alu_out.set(0)
        self.rd.set(0)
        self.pc4.set(0)
        self.wb_sel.set(False)
        self.reg_wr.set(False)
        self.valid.set(False)
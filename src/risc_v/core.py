from sim_base.clock import Clock
from sim_base.mem.register import Register
import risc_v.riscv_config as conf

#import memory modules:
from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.reg_file import RegFile

#import other modules:
from risc_v.modules.alu import Alu
from risc_v.modules.branch_unit import BranchUnit
from risc_v.modules.decode import Instruction_Decoder
from risc_v.modules.dmem_rd_port import dmem_rd_port
from risc_v.modules.dmem_wr_port import dmem_wr_port
from risc_v.modules.immgen import ImmGen
from risc_v.modules.pc import PC
from risc_v.modules.shifter import Shifter


class Core:
    def __init__(self, imem_size, dmem_size):
        self.reg_file = RegFile()
        self.dmem = DataMem(dmem_size)
        self.imem = InstrMem(imem_size)
        self.pc = PC(Register())
    def upload_instr(self, instructions: list[int]):
        self.imem.load_program(instructions)
    def upload_data(self, data: list[int]):
        self.dmem.load_data(data)
    
    def upload_instr_from_hex(self, filename: str):
        """Загружает инструкции из hex-файла (по 32 бита на строку)."""
        instructions = self._load_hex_file(filename)
        self.imem.load_program(instructions)

    def upload_data_from_hex(self, filename: str):
        """Загружает данные из hex-файла (по 32 бита на строку)."""
        data = self._load_hex_file(filename)
        self.dmem.load_data(data)

    def tick(self):
        instr = conf.Instruction(self.imem.read(self.pc.reg.read()))
        
        decoded = Instruction_Decoder.decode(instr)
        
        imm = ImmGen.generate(instr, decoded.imm_type)
        
        rd1 = self.reg_file.read(instr.rs1)
        rd2 = self.reg_file.read(instr.rs2)
        
        br_eq, br_lt = BranchUnit.compare(rd1, rd2, decoded.br_un)
        
        decoded = Instruction_Decoder.decode(instr, br_eq, br_lt)
        
        alu_in_a = rd1 if decoded.a_sel else self.pc.read()
        alu_in_b = rd2 if decoded.b_sel else imm
        
        alu_out = Alu.execute(decoded.alu_sel, alu_in_a, alu_in_b)
        
        shifter_out = Shifter.shift(rd1, instr.shamt, decoded.sh_sel)
        
        pc_plus_4 = self.pc.read()
        
        dmem_wr_port(self.dmem, alu_out, rd2, decoded.dmem_sel.funct3(), decoded.dmem_sel.is_write())
        
        match decoded.wb_sel:
            case conf.WB_sel_t.ALU_OUT:
                wd3 = alu_out
            case conf.WB_sel_t.PC4_OUT:
                wd3 = self.pc.read()+4
            case conf.WB_sel_t.SHIFTER_OUT:
                wd3 = shifter_out
            case conf.WB_sel_t.DMEM_OUT:
                wd3 = dmem_rd_port(self.dmem, alu_out, decoded.dmem_sel.func3())
            case _:
                raise ValueError(f"Invalid write back sel: {decoded.wb_sel}")
        
        self.reg_file.write(instr.rd, wd3)
        
        if decoded.reg_wr:
            self.reg_file.update()
        
        self.reg_file.update()
        self.dmem.update()
        self.imem.update()
        self.pc.set_pc(decoded.pc_sel, alu_out)
        self.pc.reg.update()
    
    
    def _load_hex_file(self, filename: str) -> list[int]:
        """Вспомогательный метод: читает hex-файл и возвращает список 32-битных чисел."""
        result = []
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # пропускаем пустые строки
                    continue
                # Убираем возможный префикс '0x' и пробелы
                clean_line = line.replace('0x', '').replace('0X', '').replace(' ', '')
                if not clean_line:
                    continue
                try:
                    # Парсим как 32-битное число (8 hex-цифр)
                    value = int(clean_line, 16)
                    # Проверяем, что значение помещается в 32 бита
                    if value > 0xFFFFFFFF:
                        raise ValueError(f"Value 0x{value:X} exceeds 32 bits at line {line_num}")
                    result.append(value)
                except ValueError as e:
                    raise ValueError(f"Invalid hex at line {line_num}: '{line}'") from e
        return result

    
    
        






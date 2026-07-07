from risc_v import core

core = core.Core(2**10, 2**10)

program = "C:\\Users\\Lecoo\\Documents\\rv-nsu\\prg\\uBench\\hex\\andi_test.hex"

core.upload_instr_from_hex(program)

for i in range(20):
    core.tick()
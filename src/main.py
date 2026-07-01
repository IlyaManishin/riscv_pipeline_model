from sim_base.mem.register import Register
from risc_v.core import clk

shift_len = 5
shift_reg = [Register() for i in range(shift_len)]
for reg in shift_reg:
    clk.add_trigger(reg)

iters = 100
for i in range(1, iters + 1):
    for j in range(shift_len):
        if (j == 0):
            shift_reg[0].set(i)
        else:
            shift_reg[j].set(shift_reg[j - 1].read())
    print(", ".join([str(r.read()) for r in shift_reg]))
    clk.tick()

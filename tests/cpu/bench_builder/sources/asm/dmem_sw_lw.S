# test01: SW / LW одного слова. RAM 0x80000000, буфер 0x80000100.
#--- 
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#---

.globl _start
_start:
        lui     a1, 0x80000
        addi    a1, a1, 0x100

        li      t0, 0x11223344
        sw      t0, 0(a1)
        lw      t1, 0(a1)
        bne     t0, t1, fail

        addi x31, x0, TEST_PASS
pass:   j       pass

fail:
        addi x31, x0, TEST_FAIL
hang:   j       hang

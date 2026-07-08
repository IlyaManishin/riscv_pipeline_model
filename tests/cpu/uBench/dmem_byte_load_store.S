# test02: SB, LB, LBU. RAM 0x80000000, буфер 0x80000100.
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

        lb      t1, 1(a1)
        li      t2, 0x33
        bne     t1, t2, fail

        lbu     t1, 1(a1)
        bne     t1, t2, fail

        li      t0, 0xAB
        sb      t0, 2(a1)
        lb      t1, 2(a1)
        li      t2, 0xFFFFFFAB
        bne     t1, t2, fail

        lbu     t1, 2(a1)
        li      t2, 0xAB
        bne     t1, t2, fail

        addi x31, x0, TEST_PASS
pass:   j       pass

fail:
        addi x31, x0, TEST_FAIL
hang:   j       hang

# test03: SH, LH, LHU (выровненные адреса). RAM 0x80000000, буфер 0x80000100.
#--- 
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#---

.globl _start
_start:
        lui     a1, 0x80000
        addi    a1, a1, 0x100

        sw      zero, 0(a1)
        li      t0, 0xA1B2
        sh      t0, 0(a1)

        lh      t1, 0(a1)
        li      t2, 0xFFFFA1B2
        bne     t1, t2, fail

        lhu     t1, 0(a1)
        li      t2, 0xA1B2
        bne     t1, t2, fail

        li      t0, 0x5566
        sh      t0, 2(a1)

        lh      t1, 2(a1)
        li      t2, 0x00005566
        bne     t1, t2, fail

        lhu     t1, 2(a1)
        li      t2, 0x5566
        bne     t1, t2, fail

        addi x31, x0, TEST_PASS
pass:   j       pass

fail:
        addi x31, x0, TEST_FAIL
hang:   j       hang

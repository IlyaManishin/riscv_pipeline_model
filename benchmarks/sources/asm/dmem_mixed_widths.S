# test05: SW затем SB (частичная запись). Буфер 0x80000100.
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

        li      t0, 0xFF
        sb      t0, 1(a1)

        lw      t1, 0(a1)
        li      t2, 0x1122FF44
        bne     t1, t2, fail

        li      t0, 0xAABBCCDD
        sw      t0, 0(a1)
        li      t0, 0xEE
        sb      t0, 3(a1)
        lw      t1, 0(a1)
        li      t2, 0xEEBBCCDD
        bne     t1, t2, fail

        addi x31, x0, TEST_PASS
pass:   j       pass

fail:
        addi x31, x0, TEST_FAIL
hang:   j       hang

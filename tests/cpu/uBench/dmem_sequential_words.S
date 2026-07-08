# test06: четыре слова по смещениям 0, 4, 8, 12. Буфер 0x80000100.
#--- 
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#---

.globl _start
_start:
        lui     a1, 0x80000
        addi    a1, a1, 0x100

        li      t0, 0xAAAABBBB
        sw      t0, 0(a1)
        li      t0, 0xCCCCDDDD
        sw      t0, 4(a1)
        li      t0, 0xEEEEFFFF
        sw      t0, 8(a1)
        li      t0, 0x01020304
        sw      t0, 12(a1)

        lw      t1, 0(a1)
        li      t2, 0xAAAABBBB
        bne     t1, t2, fail

        lw      t1, 4(a1)
        li      t2, 0xCCCCDDDD
        bne     t1, t2, fail

        lw      t1, 8(a1)
        li      t2, 0xEEEEFFFF
        bne     t1, t2, fail

        lw      t1, 12(a1)
        li      t2, 0x01020304
        bne     t1, t2, fail

        addi x31, x0, TEST_PASS
pass:   j       pass

fail:
        addi x31, x0, TEST_FAIL
hang:   j       hang

#--- 
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#---
.text
    addi x1, x0, 1
    addi x2, x0, -2
    xor  x3, x1, x2
    addi x4, x0, -1
    bne  x3, x4 fail
    or   x3, x1, x2
    bne  x3, x4 fail
    and  x3, x1, x2
    bne  x3, x0 fail
    addi x1, x0, -2
    addi x2, x0, -4
    xor  x3, x1, x2
    addi x4, x0, 2
    bne  x3, x4 fail
    or   x3, x1, x2
    bne  x3, x1 fail
    and  x3, x1, x2
    bne  x3, x2 fail

    addi x31, x0, TEST_PASS
pass:
    j pass
fail:
    addi x31, x0, TEST_FAIL
    j fail   
    
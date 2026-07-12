#------------------------------------------------------------------------------
#    simplest 'sra', 'srai' test
#------------------------------------------------------------------------------

#--- 
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#--- variable part
# case 1 vars
.eqv C1_OP1 2
.eqv C1_OP2 0
.eqv C1_RES 2
# case 2 vars
.eqv C2_OP1 -8
.eqv C2_OP2 2
.eqv C2_RES -2
# case 3 vars
.eqv C3_OP1 0
.eqv C3_OP2 5
.eqv C3_RES 0
# case 4 vars
.eqv C4_OP1 2
.eqv C4_OP2 2
.eqv C4_RES 0
# case 5 vars (sra only)
.eqv C5_OP1 2
.eqv C5_OP2 129
.eqv C5_RES 1

#------------------------------------------------------------------------------
.text
# case 1
    addi x10, x0, C1_RES
    addi x1, x0, C1_OP1
    addi x2, x0, C1_OP2
    sra  x3, x1, x2
    bne  x3, x10, test_fail
    srai x3, x1, C1_OP2
    bne  x3, x10, test_fail
# case 2
    addi x11, x0, C2_RES
    addi x4, x0, C2_OP1
    addi x5, x0, C2_OP2
    sra  x6, x4, x5
    bne  x6, x11, test_fail
    srai x6, x4, C2_OP2
    bne  x6, x11, test_fail
# case 3
    addi x12, x0, C3_RES
    addi x7, x0, C3_OP1
    addi x8, x0, C3_OP2
    sra  x9, x7, x8
    bne  x9, x12, test_fail
    srai x9, x7, C3_OP2
    bne  x9, x12, test_fail
# case 4
    addi x16, x0, C4_RES
    addi x13, x0, C4_OP1
    addi x14, x0, C4_OP2
    sra  x15, x13, x14
    bne  x15, x12, test_fail
    srai x15, x13, C4_OP2
    bne  x15, x12, test_fail
# case 5
    addi x20, x0, C5_RES
    addi x17, x0, C5_OP1
    addi x18, x0, C5_OP2
    sra  x19, x17, x18
    bne  x19, x20, test_fail
    
    addi  x31, x0, TEST_PASS

test_pass:
    jal   x0, test_pass

test_fail:
    addi  x31, x0, TEST_FAIL
    jal   x0, test_fail

    

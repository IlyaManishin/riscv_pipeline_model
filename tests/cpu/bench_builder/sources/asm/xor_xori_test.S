#------------------------------------------------------------------------------
#    simplest 'xor', 'xori' test
#------------------------------------------------------------------------------

#--- 
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#--- variable part
# case 1 vars
.eqv C1_OP1 -8
.eqv C1_OP2 -9
.eqv C1_RES 15
# case 2 vars
.eqv C2_OP1 7
.eqv C2_OP2 -7
.eqv C2_RES -2
# case 3 vars
.eqv C3_OP1 7
.eqv C3_OP2 4
.eqv C3_RES 3

#------------------------------------------------------------------------------
.text
# case 1
    addi x10, x0, C1_RES
    addi x1, x0, C1_OP1
    addi x2, x0, C1_OP2
    xor  x3, x1, x2
    bne  x3, x10, test_fail
    xori x3, x1, C1_OP2
    bne  x3, x10, test_fail
# case 2
    addi x11, x0, C2_RES
    addi x4, x0, C2_OP1
    addi x5, x0, C2_OP2
    xor  x6, x4, x5
    bne  x6, x11, test_fail
    xori x6, x4, C2_OP2
    bne  x6, x11, test_fail
# case 3
    addi x12, x0, C3_RES
    addi x7, x0, C3_OP1
    addi x8, x0, C3_OP2
    xor  x9, x7, x8
    bne  x9, x12, test_fail
    xori x9, x7, C3_OP2
    bne  x9, x12, test_fail
    
    addi x31, x0, TEST_PASS

test_pass:
    jal x0, test_pass

test_fail:
    addi x31, x0, TEST_FAIL
    jal x0, test_fail

    

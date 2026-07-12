#------------------------------------------------------------------------------
#    simplest 'jalr' test
#------------------------------------------------------------------------------

#--- 
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#------------------------------------------------------------------------------
.text
    jal x0, case1
case2_check:
    bne x17, x18, test_fail
    jal test_pass
case1:
    la x1, case1_check
    auipc x2, 0
    addi x2, x2, 12
    jalr x3, x1, 0
    jal  x0, test_fail
case1_check:
    bne x2, x3, test_fail
case2:
    la x16, case2_check
    auipc x17, 0
    addi x17, x17, 12
    jalr x18, x16, 0
    jal  x0, test_fail
   
test_pass:
    addi x31, x0, TEST_PASS
    jal x0, test_pass
test_fail:
    addi x31, x0, TEST_FAIL
    jal x0, test_fail

    

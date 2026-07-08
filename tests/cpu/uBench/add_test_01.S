#------------------------------------------------------------------------------
#    simplest 'add', 'addi' test
#------------------------------------------------------------------------------

#--- common part for all tests (proposal)
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#--- variable part (test-dependent)
.eqv OP1 1
.eqv OP2 2
.eqv RES 3

#------------------------------------------------------------------------------
.text
    addi x7, x0, RES
    addi x1, x0, OP1
    addi x2, x0, OP2
    add  x3, x2, x1
    bne  x3, x7, test_fail
    addi x31, x0, TEST_PASS

test_pass:
    jal x0, test_pass

test_fail:
    addi x31, x0, TEST_FAIL
    jal x0, test_fail

    

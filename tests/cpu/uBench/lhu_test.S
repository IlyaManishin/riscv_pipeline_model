#------------------------------------------------------------------------------
#    LHU (load half unsigned) test
#------------------------------------------------------------------------------
# Tests:
#   1. store 0 in x1, store 1 in x2, load word from DMEM. Expect: x1 == x2
#------------------------------------------------------------------------------

#--- common part for all tests (proposal)
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#------------------------------------------------------------------------------

.eqv DMEM_START_REG x10

.data
.align 4
test_mem: .space 32

.text
    la DMEM_START_REG, test_mem

    # Test 1. store 0 in x1, store 1 in x2, load word from DMEM. Expect: x1 == x2
    addi x1, x0, 0
    addi x2, x0, 1
    sh x0, 0(DMEM_START_REG)
    lhu x1, 0(DMEM_START_REG)
    lhu x2, 0(DMEM_START_REG)
    bne x1, x2, test_fail
    j test_pass

test_pass:
    addi TEST_RESULT, x0, TEST_PASS
    jal x0, test_pass

test_fail:
    addi TEST_RESULT, x0, TEST_FAIL
    jal x0, test_fail

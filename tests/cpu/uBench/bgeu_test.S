#------------------------------------------------------------------------------
#    BGEU (branch if greater or equal unsigned) test
#------------------------------------------------------------------------------
# Tests:
#   1. Branch should be taken when x1 = x2 (1 = 1)
#   2. Branch should be taken when x1 > x2 (2 > 1)
#   3. Branch should be taken when x1 > x2 (1 > 0)
#   4. Branch should not be taken when x1 < x2 (1 < 2)
#------------------------------------------------------------------------------

#--- common part for all tests (proposal)
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#------------------------------------------------------------------------------
.text
    # Test 1: Branch should be taken when x1 = x2 (1 = 1)
    addi x1, x0, 1
    addi x2, x0, 1
    bgeu x1, x2, branch_test_2
    j    test_fail

branch_test_2:
    # Test 2: Branch should be taken when x1 > x2 (2 > 1)
    addi x1, x0, 2
    addi x2, x0, 1
    bgeu x1, x2, branch_test_3
    j    test_fail

branch_test_3:
    # Test 3: Branch should be taken when x1 > x2 (1 > 0)
    addi x1, x0, 1
    addi x2, x0, 0
    bgeu x1, x2, branch_test_4
    j    test_fail

branch_test_4:
    # Test 4: Branch should not be taken when x1 < x2 (1 < 2)
    addi x1, x0, 1
    addi x2, x0, 2
    bgeu x1, x2, test_fail

test_pass:
    addi TEST_RESULT, x0, TEST_PASS
    jal x0, test_pass

test_fail:
    addi TEST_RESULT, x0, TEST_FAIL
    jal x0, test_fail

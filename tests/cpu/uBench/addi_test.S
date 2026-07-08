#----------------------------------
#	ADDI TESTBENCH
#----------------------------------

.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

.text
# test 1. 5 + 3 = 8
	addi x1, x0, 5
	addi x1, x1, 3
	li x2, 8
	bne x1, x2, test_fail

# test 2. 5 - 3 = 2
	addi x1, x0, 5
	addi x1, x1, -3
	li x2, 2
	bne x1, x2, test_fail

# test 3. 10 + 0 = 10
	addi x1, x0, 10
	addi x1, x1, 0
	li x2, 10
	bne x1, x2, test_fail

test_pass:
	addi TEST_RESULT, x0, TEST_PASS
	jal x0, test_pass

test_fail:
	addi TEST_RESULT, x0, TEST_FAIL
	jal x0, test_fail
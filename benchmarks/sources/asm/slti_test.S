#----------------------------------
#	SLTI TESTBENCH
#----------------------------------

.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

.text
# test 1. 5 < 10 -> 1
	addi x1, x0, 5
	slti x3, x1, 10
	li x2, 1
	bne x3, x2, test_fail

# test 2. 10 < 5 -> 0
	addi x1, x0, 10
	slti x3, x1, 5
	li x2, 0
	bne x3, x2, test_fail

# test 3. 5 < 5 -> 0
	addi x1, x0, 5
	slti x3, x1, 5
	li x2, 0
	bne x3, x2, test_fail

# test 4. -5 < 5 -> 1
	addi x1, x0, -5
	slti x3, x1, 5
	li x2, 1
	bne x3, x2, test_fail

test_pass:
	addi TEST_RESULT, x0, TEST_PASS
	jal x0, test_pass

test_fail:
	addi TEST_RESULT, x0, TEST_FAIL
	jal x0, test_fail
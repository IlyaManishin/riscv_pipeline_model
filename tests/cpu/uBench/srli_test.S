#----------------------------------
#	SRLI TESTBENCH
#----------------------------------

.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

.text
# test 1. 16 >> 2 = 4
	addi x1, x0, 16
	srli x3, x1, 2
	li x2, 4
	bne x3, x2, test_fail

# test 2. 16 >> 0 = 16
	addi x1, x0, 16
	srli x3, x1, 0
	li x2, 16
	bne x3, x2, test_fail

# test 3. 32 >> 5 = 1
	addi x1, x0, 32
	srli x3, x1, 5
	li x2, 1
	bne x3, x2, test_fail

# test 4. 0x80000000 >> 1 = 0x40000000 
	li x1, 0x80000000
	srli x3, x1, 1
	li x2, 0x40000000
	bne x3, x2, test_fail
	j test_pass

test_pass:
	addi TEST_RESULT, x0, TEST_PASS
	jal x0, test_pass

test_fail:
	addi TEST_RESULT, x0, TEST_FAIL
	jal x0, test_fail

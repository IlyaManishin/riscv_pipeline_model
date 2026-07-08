#----------------------------------
#    JAL TESTBENCH
#----------------------------------

#--- common part for all tests (proposal)
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

.text
	addi a0, x0, 2

# Test 1. 1st call: 2 * 2 = 4
	jal adder
	li x3, 4
	bne a0, x3, test_fail

# Test 2. 2nd call: 4 * 2 = 8
	jal adder
	li x3, 8
	bne a0, x3, test_fail

# Test 3. 3rd call: 8 * 2 = 16
	jal adder
	li x3, 16
	bne a0, x3, test_fail

# Test 4. 4th call: 16 * 2 = 32
	jal adder
	li x3, 32
	bne a0, x3, test_fail

# Test 5. 5th call: 32 * 2 = 64
	jal adder
	li x3, 64
	bne a0, x3, test_fail

	j test_pass

adder:
	add a0, a0, a0        
	jalr x0, 0(x1)              

test_pass:
	addi TEST_RESULT, x0, TEST_PASS
	jal x0, test_pass

test_fail:
	addi TEST_RESULT, x0, TEST_FAIL
	jal x0, test_fail
#----------------------------------
#	ORI TESTBENCH
#----------------------------------

.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

.text
# test 1. 0xAA | 0x0F = 0xAF
	li x1, 0xAA
	ori x3, x1, 0x0F
	li x2, 0xAF
	bne x3, x2, test_fail

# test 2. 0xFF | 0 = 0xFF
	li x1, 0xFF
	ori x3, x1, 0
	li x2, 0xFF
	bne x3, x2, test_fail

# test 3. 0 | 0x55 = 0x55
	li x1, 0
	ori x3, x1, 0x55
	li x2, 0x55
	bne x3, x2, test_fail

# test 4. 0x12 | 0 = 0x12
	li x1, 0x12
	ori x3, x1, 0
	li x2, 0x12
	bne x3, x2, test_fail

# test 5. 0xF0 | 0x0F = 0xFF
	li x1, 0xF0
	ori x3, x1, 0x0F
	li x2, 0xFF
	bne x3, x2, test_fail
	j test_pass

test_pass:
	addi TEST_RESULT, x0, TEST_PASS
	jal x0, test_pass

test_fail:
	addi TEST_RESULT, x0, TEST_FAIL
	jal x0, test_fail
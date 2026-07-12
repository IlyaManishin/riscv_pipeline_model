#----------------------------------
#    SB (store byte) test
#----------------------------------

#--- common part for all tests (proposal)
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

.eqv BASE_ADDR 0x80000000

.text
    li x10, BASE_ADDR
    li x1, 0x12345678
    li x2, 0x89ABCDEF

# Test 1. SB positive byte (0x78) -> LB/LBU check
    sb x1, 0(x10)
    lb x3, 0(x10)
    li x4, 0x00000078
    bne x3, x4, test_fail
    lbu x5, 0(x10)
    li x6, 0x00000078
    bne x5, x6, test_fail

# Test 2. SB negative byte (0xEF) -> LB/LBU check
    sb x2, 4(x10)
    lb x3, 4(x10)
    li x4, 0xFFFFFFEF
    bne x3, x4, test_fail
    lbu x5, 4(x10)
    li x6, 0x000000EF
    bne x5, x6, test_fail
    j test_pass

# Test 3. SB zero byte
    li x1, 0x00000000
    sb x1, 8(x10)
    lb x3, 8(x10)
    li x4, 0x00000000
    bne x3, x4, test_fail
    lbu x5, 8(x10)
    li x6, 0x00000000
    bne x5, x6, test_fail

test_pass:
    addi TEST_RESULT, x0, TEST_PASS
    jal x0, test_pass

test_fail:
    addi TEST_RESULT, x0, TEST_FAIL
    jal x0, test_fail

#----------------------------------
#    SW (store word) test
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

# Test 1. SW positive word (0x12345678) -> LW check
    sw x1, 0(x10)
    lw x3, 0(x10)
    li x4, 0x12345678
    bne x3, x4, test_fail
    lw x5, 0(x10)
    li x6, 0x12345678
    bne x5, x6, test_fail

# Test 2. SW negative word (0x89ABCDEF) -> LW check
    sw x2, 4(x10)
    lw x3, 4(x10)
    li x4, 0x89ABCDEF
    bne x3, x4, test_fail
    lw x5, 4(x10)
    li x6, 0x89ABCDEF
    bne x5, x6, test_fail
    j test_pass

# Test 3. SW zero word
    li x1, 0x00000000
    sw x1, 8(x10)
    lw x3, 8(x10)
    li x4, 0x00000000
    bne x3, x4, test_fail
    lw x5, 8(x10)
    li x6, 0x00000000
    bne x5, x6, test_fail

test_pass:
    addi TEST_RESULT, x0, TEST_PASS
    jal x0, test_pass

test_fail:
    addi TEST_RESULT, x0, TEST_FAIL
    jal x0, test_fail

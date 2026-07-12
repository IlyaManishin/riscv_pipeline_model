#------------------------------------------------------------------------------
#    LB + SB (load byte + store byte) interaction test
#------------------------------------------------------------------------------
# Tests:
#   1. store 0xAB, load back, expect 0xFFFFFFAB
#   2. store 0x80 (-128), load back, expect 0xFFFFFF80
#   3. store 0x7F (+127), load back, expect 0x0000007F
#   4. multiple bytes at different offsets
#   5. sb doesn't affect adjacent bytes
#------------------------------------------------------------------------------

#--- common part for all tests (proposal)
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

.eqv DMEM_START_REG x10

.data
.align 4
test_mem: .space 4

.text
    la DMEM_START_REG, test_mem
    # Test 1. store 0xAB, load back, expect 0xFFFFFFAB
    addi x3, x0, 0xAB
    sb x3, 0(DMEM_START_REG)
    lb x1, 0(DMEM_START_REG)
    addi x2, x0, 0xFFFFFFAB
    bne x1, x2, test_fail

    # Test 2. store 0x80 (-128), load back, expect 0xFFFFFF80
    addi x3, x0, 0xFFFFFF80
    sb x3, 0(DMEM_START_REG)
    lb x1, 0(DMEM_START_REG)
    addi x2, x0, 0xFFFFFF80
    bne x1, x2, test_fail

    # Test 3. store 0x7F (+127), load back, expect 0x0000007F
    addi x3, x0, 0x7F
    sb x3, 0(DMEM_START_REG)
    lb x1, 0(DMEM_START_REG)
    addi x2, x0, 0x7F
    bne x1, x2, test_fail

    # Test 4. multiple bytes at different offsets
    addi x3, x0, 0x11
    sb x3, 0(DMEM_START_REG)
    addi x3, x0, 0x22    # will be used in Test 5.
    sb x3, 1(DMEM_START_REG)
    addi x3, x0, 0x33
    sb x3, 2(DMEM_START_REG)

    lb x1, 0(DMEM_START_REG)
    addi x2, x0, 0x11
    bne x1, x2, test_fail

    lb x1, 1(DMEM_START_REG)
    addi x2, x0, 0x22
    bne x1, x2, test_fail

    lb x1, 2(DMEM_START_REG)
    addi x2, x0, 0x33
    bne x1, x2, test_fail

    # Test 5. sb doesn't affect adjacent bytes
    addi x3, x0, 0xFF
    sb x3, 0(DMEM_START_REG)
    lb x1, 1(DMEM_START_REG)
    addi x2, x0, 0x22    # should still be 0x22 from Test 4.
    bne x1, x2, test_fail
    j test_pass

test_pass:
    addi TEST_RESULT, x0, TEST_PASS
    jal x0, test_pass

test_fail:
    addi TEST_RESULT, x0, TEST_FAIL
    jal x0, test_fail

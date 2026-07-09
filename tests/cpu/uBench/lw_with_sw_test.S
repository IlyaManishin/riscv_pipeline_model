#------------------------------------------------------------------------------
#    LW + SW (load word + store word) interaction test
#------------------------------------------------------------------------------
# Tests:
#   1. store 0xDEADB33f, load back, expect 0xDEADB33f
#   2. store 0x12345678, load back, expect 0x12345678
#   3. store -1, load back, expect 0xFFFFFFFF
#   4. multiple words at different offsets
#   5. sw doesn't affect adjacent words
#------------------------------------------------------------------------------

#--- common part for all tests (proposal)
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

.eqv DMEM_START_REG x10

.data
.align 4
test_mem: .space 24

.text
    la DMEM_START_REG, test_mem
    # Test 1. store 0xDEADB33f, load back, expect 0xDEADB33f
    lui x3, 0xDEADB
    addi x3, x3, 0x33f
    sw x3, 0(DMEM_START_REG)
    lw x1, 0(DMEM_START_REG)
    lui x2, 0xDEADB
    addi x2, x2, 0x33f
    bne x1, x2, test_fail

    # Test 2. store 0x12345678, load back, expect 0x12345678
    lui x3, 0x12345
    addi x3, x3, 0x678
    sw x3, 0(DMEM_START_REG)
    lw x1, 0(DMEM_START_REG)
    lui x2, 0x12345
    addi x2, x2, 0x678
    bne x1, x2, test_fail

    # Test 3. store -1, load back, expect 0xFFFFFFFF
    addi x3, x0, -1
    sw x3, 0(DMEM_START_REG)
    lw x1, 0(DMEM_START_REG)
    addi x2, x0, -1
    bne x1, x2, test_fail

    # Test 4. multiple words at different offsets
    lui x3, 0x77777
    addi x3, x3, 0x777
    sw x3, 0(DMEM_START_REG)
    lui x3, 0x66666
    addi x3, x3, 0x666    # will be used in Test 5.
    sw x3, 4(DMEM_START_REG)
    lui x3, 0x55555
    addi x3, x3, 0x555
    sw x3, 8(DMEM_START_REG)

    lw x1, 0(DMEM_START_REG)
    lui x2, 0x77777
    addi x2, x2, 0x777
    bne x1, x2, test_fail

    lw x1, 4(DMEM_START_REG)
    lui x2, 0x66666
    addi x2, x2, 0x666
    bne x1, x2, test_fail

    lw x1, 8(DMEM_START_REG)
    lui x2, 0x55555
    addi x2, x2, 0x555
    bne x1, x2, test_fail

    # Test 5. sw doesn't affect adjacent words
    lui x3, 0xDEADB
    addi x3, x3, 0x33f
    sw x3, 0(DMEM_START_REG)
    lw x1, 4(DMEM_START_REG)
    lui x2, 0x66666
    addi x2, x2, 0x666    # should still be 0x66666666 from Test 4.
    bne x1, x2, test_fail
    j test_pass

test_pass:
    addi TEST_RESULT, x0, TEST_PASS
    jal x0, test_pass

test_fail:
    addi TEST_RESULT, x0, TEST_FAIL
    jal x0, test_fail

#------------------------------------------------------------------------------
#    LH + SH (load halfword + store halfword) interaction test
#------------------------------------------------------------------------------
# Tests:
#   1. store 0x8000 (-32768), load back, expect 0xFFFF8000
#   2. store 0x7FFF (+32767), load back, expect 0x00007FFF
#   3. store 0xFFFF (-1), load back, expect 0xFFFFFFFF
#   4. multiple halfwords at different offsets
#   5. sh doesn't affect bytes outside halfword
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
    # Test 1. store 0x8000 (-32768), load back, expect 0xFFFF8000
    lui x3, 0xFFFF8
    addi x3, x3, 0x000
    sh x3, 0(DMEM_START_REG)
    lh x1, 0(DMEM_START_REG)
    lui x2, 0xFFFF8
    addi x2, x2, 0x000
    bne x1, x2, test_fail

    # Test 2. store 0x7FFF (+32767), load back, expect 0x00007FFF
    lui x3, 0x0007
    addi x3, x3, 0x3FF
    sh x3, 0(DMEM_START_REG)
    lh x1, 0(DMEM_START_REG)
    lui x2, 0x00007
    addi x2, x2, 0x3FF
    bne x1, x2, test_fail

    # Test 3. store 0xF3FF (-1), load back, expect 0xFFFFF3FF
    lui x3, 0x0000F
    addi x3, x3, 0x3FF
    sh x3, 0(DMEM_START_REG)
    lh x1, 0(DMEM_START_REG)
    lui x2, 0xFFFFF
    addi x2, x2, 0x3FF
    bne x1, x2, test_fail

    # Test 4. multiple halfwords at different offsets
    lui x3, 0x00001
    addi x3, x3, 0x234
    sh x3, 0(DMEM_START_REG)
    lui x3, 0x00005
    addi x3, x3, 0x678 # will be used in Test 5.
    sh x3, 2(DMEM_START_REG)

    lh x1, 0(DMEM_START_REG)
    lui x2, 0x00001
    addi x2, x2, 0x234
    bne x1, x2, test_fail

    lh x1, 2(DMEM_START_REG)
    lui x2, 0x00005
    addi x2, x2, 0x678
    bne x1, x2, test_fail

    # Test 5. sh doesn't affect bytes outside halfword
    lui x3, 0xFFFF0
    addi x3, x3, 0x000
    sh x3, 0(DMEM_START_REG)    # write 0xFFFF to bytes 0-1
    lh x1, 2(DMEM_START_REG)    # read bytes 2-3
    lui x2, 0x00005
    addi x2, x2, 0x678    # should still be 0x5678 from Test 4.
    bne x1, x2, test_fail
    j test_pass

test_pass:
    addi TEST_RESULT, x0, TEST_PASS
    jal x0, test_pass

test_fail:
    addi TEST_RESULT, x0, TEST_FAIL
    jal x0, test_fail

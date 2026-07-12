#------------------------------------------------------------------------------
#    DMEM integration test (store insns: S[W|H|B], load insns: L[W|H|HU|B|BU])
#------------------------------------------------------------------------------
# Tests:
#   1. Word tests: SW, LW
#   2. Half tests: SH, LH, LHU
#   3. Byte tests: SB, LB, LBU
#------------------------------------------------------------------------------

#--- common part for all tests (proposal)
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#------------------------------------------------------------------------------

.eqv DMEM_START_REG x10
.eqv DMEM_LOAD_REG  x3
.eqv EXPECT_REG     x4

.data
.align 4
test_mem: .space 32

.text
    la DMEM_START_REG, test_mem

    # Init
    li x1, 0x12345678
    li x2, 0x89ABCDEF

    # Test 1. Word tests: SW, LW
    sw x1, 0(DMEM_START_REG)
    lw DMEM_LOAD_REG, 0(DMEM_START_REG)         # Expect: 0x12345678
    li EXPECT_REG, 0x12345678
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail
    sw x2, 4(DMEM_START_REG)
    lw DMEM_LOAD_REG, 4(DMEM_START_REG)         # Expect: 0x89ABCDEF
    li EXPECT_REG, 0x89ABCDEF
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail

    # Test 2. Half tests: SH, LH, LHU
    sh x1, 8(DMEM_START_REG)                    # Store 0x5678
    lh DMEM_LOAD_REG, 8(DMEM_START_REG)         # Expect: 0x00005678 (sign-extend)
    li EXPECT_REG, 0x00005678
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail
    lhu DMEM_LOAD_REG, 8(DMEM_START_REG)        # Expect: 0x00005678 (zero-extend)
    li EXPECT_REG, 0x00005678
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail
    sh x2, 12(DMEM_START_REG)                   # Store 0xCDEF
    lh DMEM_LOAD_REG, 12(DMEM_START_REG)        # Expect: 0xFFFFCDEF
    li EXPECT_REG, 0xFFFFCDEF
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail
    lhu DMEM_LOAD_REG, 12(DMEM_START_REG)       # Expect: 0x0000CDEF
    li EXPECT_REG, 0x0000CDEF
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail

    # Test 3. Byte tests: SB, LB, LBU
    sb x1, 16(DMEM_START_REG)                   # Store 0x78
    lb DMEM_LOAD_REG, 16(DMEM_START_REG)        # Expect: 0x00000078
    li EXPECT_REG, 0x00000078
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail
    lbu DMEM_LOAD_REG, 16(DMEM_START_REG)       # Expect: 0x00000078
    li EXPECT_REG, 0x00000078
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail
    sb x2, 20(DMEM_START_REG)                   # Store 0xEF
    lb DMEM_LOAD_REG, 20(DMEM_START_REG)        # Expect: 0xFFFFFFEF
    li EXPECT_REG, 0xFFFFFFEF
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail
    lbu DMEM_LOAD_REG, 20(DMEM_START_REG)       # Expect: 0x000000EF
    li EXPECT_REG, 0x000000EF
    bne DMEM_LOAD_REG, EXPECT_REG, test_fail
    j test_pass

test_pass:
    addi TEST_RESULT, x0, TEST_PASS
    jal x0, test_pass

test_fail:
    addi TEST_RESULT, x0, TEST_FAIL
    jal x0, test_fail

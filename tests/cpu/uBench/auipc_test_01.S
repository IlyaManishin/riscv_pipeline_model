#------------------------------------------------------------------------------
#    simplest 'auipc' test
#------------------------------------------------------------------------------
# This test uses an architectural feature - 4 bytes per instruction.

.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

# case 1
.eqv C1_IMM 0x1
.eqv C1_IMM_SHIFT 0x1000

# case 2
.eqv C2_IMM 0x1B
.eqv C2_IMM_SHIFT 0x1B000

# case 3
.eqv C3_IMM 0x0
.eqv C3_IMM_SHIFT 0x0

#------------------------------------------------------------------------------
.text

# case 1
    auipc x1, C1_IMM
    auipc x2, 0
    sub   x3, x1, x2
    addi x3, x3, 4 # adding a difference
    li  x10, C1_IMM_SHIFT
    bne   x3, x10, test_fail

# case 2
    auipc x4, C2_IMM
    auipc x5, 0
    sub   x6, x4, x5
    addi x6, x6, 4 # adding a difference
    li  x11, C2_IMM_SHIFT
    bne   x6, x11, test_fail

# case 3
    auipc x7, C3_IMM
    auipc x8, 0
    sub   x9, x7, x8
    addi x9, x9, 4 # adding a difference
    li  x12, C3_IMM_SHIFT
    bne   x9, x12, test_fail

    addi x31, x0, TEST_PASS

test_pass:
    jal x0, test_pass

test_fail:
    addi x31, x0, TEST_FAIL
    jal x0, test_fail

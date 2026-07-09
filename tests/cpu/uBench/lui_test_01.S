#------------------------------------------------------------------------------
#    simplest 'lui' test
#------------------------------------------------------------------------------

.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

# case 1
.eqv C1_IMM 0x12345
.eqv C1_RES 0x12345000

# case 2
.eqv C2_OPIMM_1_a 0xCE
.eqv C2_OPIMM_1_b -0x7B8
.eqv C2_OPIMM_2 0xB7F
.eqv C2_RES 0x848 # 0xCE848 and 0xB7F = 0x848

# case 3
.eqv C3_OP1 0xBDB345
.eqv C3_OP2 0xFF424CBB # (0xFF424CBB = 0 - 0xBDB345)
.eqv C3_RES 0x0

#------------------------------------------------------------------------------
.text
# case 1
    lui  x1, C1_IMM
    lui  x10, C1_IMM
    bne  x1, x10, test_fail

# case 2 assembling 32 bits
    lui  x2, C2_OPIMM_1_a
    addi x2, x2, C2_OPIMM_1_b
    li x3, C2_OPIMM_2
    li x11 C2_RES

    and x4, x2, x3
    bne  x4, x11, test_fail

# case 3
    li  x3, C3_OP1 # the Assembler replaces li with lui+addi (if the value is large)
    li  x4, C3_OP2
    li  x12, C3_RES 
    add x5, x3, x4
    bne  x5, x12, test_fail

    addi x31, x0, TEST_PASS

test_pass:
    jal x0, test_pass

test_fail:
    addi x31, x0, TEST_FAIL
    jal x0, test_fail
#----------------------------------
#	SHIFT TEST
#----------------------------------
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#----------------------------------
#  Case 1: BitsCount
#----------------------------------
.eqv C1_IN   0xF0F0F00F
.eqv C1_RES  16

.eqv M1      0x55555555
.eqv M2      0x33333333
.eqv M4      0x0F0F0F0F
.eqv M8      0x00FF00FF
.eqv M16     0x0000FFFF

#----------------------------------
#  Case 2: Signed Right Shift >>> арифметический сдвиг (srai)
#----------------------------------
.eqv C2_IN   0x80000001
.eqv C2_RES  0xF0000000

#----------------------------------
#  Case 3: Logical Left Shift << и комбинированные операции
#----------------------------------
.eqv C3_IN   0x00000013
.eqv C3_RES  0x00000130 

.text

#----------------------------------
# Case 1: bits count
#----------------------------------
    li x1, C1_IN
    li x10, C1_RES
    li x11, M1
    li x12, M2
    li x13, M4
    li x14, M8
    li x15, M16

    # Step 1: count bits in pairs
    srli x2, x1, 1
    and  x2, x2, x11
    and  x1, x1, x11
    add  x1, x1, x2

    # Step 2: count bits in nibbles (4-bit blocks)
    srli x2, x1, 2
    and  x2, x2, x12
    and  x1, x1, x12
    add  x1, x1, x2

    # Step 3: count bits in bytes (8-bit blocks)
    srli x2, x1, 4
    and  x2, x2, x13
    and  x1, x1, x13
    add  x1, x1, x2

    # Step 4: count bits in 16-bit blocks
    srli x2, x1, 8
    and  x2, x2, x14
    and  x1, x1, x14
    add  x1, x1, x2

    # Step 5: count bits in 32-bit word
    srli x2, x1, 16
    and  x2, x2, x15
    and  x1, x1, x15
    add  x1, x1, x2

    bne  x1, x10, test_fail

#----------------------------------
# Case 2: Signed Right Shift (SRAI) с проверкой знака
#----------------------------------
    li x4, C2_IN
    li x11, C2_RES

    srai x5, x4, 1
    srai x5, x5, 1
    srai x5, x5, 1
    bne  x5, x11, test_fail

#----------------------------------
# Case 3: Logical Left Shift (SLLI) + комбинации с ADD/OR
#----------------------------------
    li x7, C3_IN
    li x12, C3_RES

    slli x8, x7, 2
    slli x8, x8, 2
    and  x8, x8, x12
    bne  x8, x12, test_fail

# PASS
    addi x31, x0, TEST_PASS
test_pass:
    jal x0, test_pass

test_fail:
    addi x31, x0, TEST_FAIL
    jal x0, test_fail

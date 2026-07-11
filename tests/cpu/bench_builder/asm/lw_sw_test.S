#----------------------------------
#   MEMORY DEPTH & WIDTH TEST
#----------------------------------
.eqv TEST_RESULT x31
.eqv TEST_PASS   1
.eqv TEST_FAIL   2

.eqv BASE_ADDR   0x80000000
.eqv PATTERN_32  0x12345678
.eqv PATTERN_16  0xABCD
.eqv PATTERN_8   0xEF

.text
    li x10, BASE_ADDR
    li x11, PATTERN_32
    li x12, PATTERN_16
    li x13, PATTERN_8

#----------------------------------
# Case 1: Word test (32-bit)
#----------------------------------
    sw   x11, 0(x10)
    lw   x20, 0(x10)
    bne  x20, x11, test_fail

#----------------------------------
# Case 2: Half-word test (16-bit)
#----------------------------------
    sh   x12, 4(x10)
    lh   x21, 4(x10)
    
    # Check sign extension
    li   x14, 0xFFFFABCD
    bne  x21, x14, test_fail
    
    # Check unsigned load
    lhu  x22, 4(x10)
    bne  x22, x12, test_fail

#----------------------------------
# Case 3: Byte test (8-bit)
#----------------------------------
    sb   x13, 8(x10)
    lb   x23, 8(x10)
    
    # Check sign extension
    li   x15, 0xFFFFFFEF
    bne  x23, x15, test_fail
    
    # Check unsigned load
    lbu  x24, 8(x10)
    bne  x24, x13, test_fail

#----------------------------------
# Case 4: Partial Write (Byte-in-Word)
#----------------------------------
    li   x25, 0xAABBCCDD
    sw   x25, 12(x10)
    li   x26, 0xFF
    sb   x26, 12(x10)      
    
    lw   x27, 12(x10)
    li   x28, 0xAABBCCFF
    bne  x27, x28, test_fail

# PASS
    addi x31, x0, TEST_PASS
test_succ:
    jal x0, test_succ

test_fail:
    addi x31, x0, TEST_FAIL
    jal x0, test_fail
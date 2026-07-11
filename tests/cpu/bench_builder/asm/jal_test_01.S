#------------------------------------------------------------------------------
#    'jal' test
#------------------------------------------------------------------------------

#--- 
.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1

#--- variable part
# case 1: simple jump forward and back
.eqv C1_START 0
.eqv C1_STOP  10
.eqv C1_RES   10

# case 2: jump to subroutine and return
.eqv C2_OP1   5
.eqv C2_OP2   3
.eqv C2_RES   8

# case 3: nested jumps
.eqv C3_OP1   7
.eqv C3_OP2   4
.eqv C3_RES   11

#------------------------------------------------------------------------------
.text

# case 1: loop using jal
    li   x1, C1_START
    li   x2, C1_STOP
    li   x10, C1_RES

case1_loop:
    addi x1, x1, 1
    blt  x1, x2, case1_loop_next
    j    case1_check
case1_loop_next:
    jal  x0, case1_loop

case1_check:
    bne  x1, x10, test_fail

# case 2: subroutine call and return
    li   x11, C2_RES
    li   x4, C2_OP1
    li   x5, C2_OP2

    jal  x12, case2_adder

    bne  x13, x11, test_fail

# case 3: nested subroutine calls
    li   x14, C3_RES
    li   x7, C3_OP1
    li   x8, C3_OP2

    jal  x15, case3_adder_nested

    bne  x16, x14, test_fail

    addi x31, x0, TEST_PASS
    j    test_pass

#------------------------------------------------------------------------------
# subroutines
case2_adder:
    add  x13, x4, x5
    jalr x0, 0(x12)

case3_adder_nested:
    jal  x17, case3_inner
    jalr x0, 0(x15)

case3_inner:
    add  x16, x7, x8
    jalr x0, 0(x17)

#------------------------------------------------------------------------------
test_pass:
    jal x0, test_pass

test_fail:
    addi x31, x0, TEST_FAIL
    jal x0, test_fail

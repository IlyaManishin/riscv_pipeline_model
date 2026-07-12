	.option nopic
	.attribute arch, "rv32i2p1"
	.text
	.section	.text.start,"ax",@progbits
	.align	4
	.globl	_start
	.type	_start, @function
_start:
    # Global pointer init
    lui     gp, %hi(__global_pointer$)
    addi    gp, gp, %lo(__global_pointer$)

    # Stack pointer init
    lui     sp, %hi(__stack_top)
    addi    sp, sp, %lo(__stack_top)

    # BSS Ranges
    lui     a5, %hi(__BSS_START__)
    addi    a5, a5, %lo(__BSS_START__)
    lui     a4, %hi(__BSS_END__)
    addi    a4, a4, %lo(__BSS_END__)

bss_init_loop:
    # If a5 >= a4, BSS is cleared, jump to main
    bgeu    a5, a4, prog_run
    
    # Clear bss
    sb      zero, 0(a5)
    addi    a5, a5, 1
    j       bss_init_loop

prog_run:
    call    main

.fin_loop:
    nop
    j       .fin_loop



OUTPUT_ARCH( "riscv" )
MEMORY
{
   imem   (x): ORIGIN = 0x40000000, LENGTH = 32768
   dmem  (rw): ORIGIN = 0x80000000, LENGTH = 16384
}

ENTRY( _start)

STACK_SIZE    = 128;
__stack_start = ORIGIN(dmem) + LENGTH(dmem) - STACK_SIZE;

SECTIONS
{
    .text :
    {
        . = ORIGIN(imem);
        *(.text.start)
        *(.text .text.*)
    } > imem
    
    . = ORIGIN(dmem);

    .rodata ALIGN(4) :
    {
        *(.rodata .rodata.*)
    } > dmem

    .data ALIGN(4) :
    {
        *(.data .data.*)
    } > dmem
    
    .sdata ALIGN(4) :
    {
        __SDATA_START__ = .;
        *(.sdata .sdata.*)
        *(.srodata .srodata.*)

        # add sbss as sdata
        . = ALIGN(4);
        __BSS_START__ = .;
        *(.sbss .sbss.* )
        
        __SDATA_END__ = .;
        __global_pointer$ = (__SDATA_START__ + __SDATA_END__) / 2;
    } > dmem
    
    .bss ALIGN(4) :
    {
        *(.bss  .bss.*)
        *(COMMON)
        . = ALIGN(4);
        __BSS_END__ = .;
    } > dmem

    .stack __stack_start :
    {    
        . = . + STACK_SIZE;
        __stack_top = .;
    } > dmem

    /DISCARD/ :
    {
        *(.comment)
        *(.riscv.attributes)
    }
}

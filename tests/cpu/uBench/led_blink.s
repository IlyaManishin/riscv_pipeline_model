#----------------------------------
#	LED BLINKING TEST
#----------------------------------

.eqv DMEM_PORT_ADDR 0x1000
.eqv BLINK_PERIOD 50000000
#.eqv BLINK_PERIOD 2

.eqv TEST_RESULT x31
.eqv TEST_FAIL   2
.eqv TEST_PASS   1
.eqv NUM_PASS    10

.text
start:
    li x1, 0
    li x2, DMEM_PORT_ADDR
    li x3, BLINK_PERIOD
    li x10, NUM_PASS

loop:
    sw x1, 0(x2)          
    addi x1, x1, 1        
    li x4, BLINK_PERIOD

    #---------------------------------------------
    #ble x1, x10, delay
    addi TEST_RESULT, x0, TEST_PASS 

delay:
    addi x4, x4, -1
    bnez x4, delay
    
    j loop

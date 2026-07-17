#define SIZE 64

/* volatile forces real memory accesses to test data hazards and cache */
volatile int data_arr[SIZE];
volatile int ptr_chase[SIZE];

static inline void finish_test(int status) {
    __asm__ __volatile__(
        "mv x31, %0\n"
        "1: nop\n"     
        "j 1b\n"
        : : "r" (status)
    );
}

int main(void) {
    int i;
    int sum = 0;
    
    /* PHASE 1: RAW Hazards & Stores */
    for (i = 0; i < SIZE; i++) {
        int a = i << 1;
        int b = a + 5;
        data_arr[i] = b;    
        
        ptr_chase[i] = (i + 1) & 63;
    }
    
    /* PHASE 2: Load-Use Hazards (Pointer Chasing) */
    volatile int curr = 0;
    for (i = 0; i < SIZE; i++) {
        curr = ptr_chase[curr];  /* LOAD */
        sum += curr;             /* USE (Requires Pipeline Stall) */
    }
    
    /* Expected sum of elements 0..63 is 2016 */
    if (sum != 2016) {
        finish_test(2);
    }
    
    /* PHASE 3: Control Hazards (Branching) */
    int evens = 0;
    int odds = 0;
    for (i = 0; i < SIZE; i++) {
        int val = data_arr[i]; 
        
        if (i & 1) { 
            odds += val; 
        } else {     
            evens += val;
        }
    }
    
    /* PHASE 4: Final Verification */
    if (evens == 2144 && odds == 2208) {
        finish_test(1); /* PASS */
    } else {
        finish_test(2); /* FAIL */
    }
    
    return 0;
}
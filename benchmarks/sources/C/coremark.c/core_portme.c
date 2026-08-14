#include "coremark.h"

/* Default thread count for multi-threading support */
ee_u32 default_num_contexts = 1;

/* Volatile seeds for SEED_METHOD == SEED_VOLATILE */
volatile ee_s32 seed1_volatile = 0x3415;
volatile ee_s32 seed2_volatile = 0x3415;
volatile ee_s32 seed3_volatile = 0x66;
volatile ee_s32 seed4_volatile = 10;   /* Number of iterations */
volatile ee_s32 seed5_volatile = 0;    /* Execs mask (0 = execute all algorithms) */

/* Read CPU cycles using RISC-V CSR mcycle register */
static inline ee_u32 get_cycles(void) {
    ee_u32 cycles;
    __asm__ __volatile__ ("csrr %0, mcycle" : "=r"(cycles));
    return cycles;
}

void start_time(void) {
    /* No initialization required for mcycle */
}

void stop_time(void) {
    /* No action required */
}

CORE_TICKS get_time(void) {
    return (CORE_TICKS)get_cycles();
}

secs_ret time_in_secs(CORE_TICKS ticks) {
    return (secs_ret)ticks;
}

/* Printf stub for bare-metal targets without stdout */
int ee_printf(const char *format, ...) {
    (void)format;
    return 0;
}

/* Memory alignment helper (4-byte alignment for RV32) */
void *align_mem(void *p) {
    return (void *)(((ee_ptr_int)p + 3) & ~3);
}

/* Heap memory allocation stubs */
void *portable_malloc(ee_size_t size) {
    (void)size;
    return 0;
}

void portable_free(void *p) {
    (void)p;
}

/* Platform initialization and cleanup hooks */
void portable_init(core_portable *p, int *argc, char *argv[]) {
    (void)argc;
    (void)argv;
    p->portable_id = 1;
}

void portable_fini(core_portable *p) {
    p->portable_id = 0;
}
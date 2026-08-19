#ifndef CORE_PORTME_H
#define CORE_PORTME_H

/* Standard NULL definition if stddef.h is not used */
#ifndef NULL
#define NULL ((void *)0)
#endif

/* Data types for 32-bit RISC-V architecture */
typedef unsigned char      ee_u8;
typedef signed short       ee_s16;
typedef unsigned short     ee_u16;
typedef signed int         ee_s32;
typedef unsigned int       ee_u32;
typedef unsigned int       ee_size_t;
typedef unsigned int       ee_ptr_int;
typedef unsigned int       CORE_TICKS;

/* Configuration options */
#define HAS_STDIO           0
#define HAS_PRINTF          0
#define HAS_FLOAT           0
#define HAS_TIME_H          0

#define COMPILER_VERSION    "GCC RV32"
#define COMPILER_FLAGS      "-O2"
#define MEM_LOCATION        "STACK"

/* Memory allocation method: 0=STATIC, 1=MALLOC, 2=STACK */
#define MEM_METHOD          2 /* MEM_STACK */

/* Seed initialization method: 0=ARG, 1=FUNC, 2=VOLATILE */
#define SEED_METHOD         2 /* SEED_VOLATILE */

#ifndef MULTITHREAD
#define MULTITHREAD         1
#endif

#ifndef MAIN_HAS_NORETURN
#define MAIN_HAS_NORETURN   0
#endif

#define MAIN_HAS_NOARGC     1

typedef struct CORE_PORTABLE_S {
    ee_u8 portable_id;
} core_portable;

/* External global variables defined in core_portme.c */
extern ee_u32 default_num_contexts;

/* Function declarations required by CoreMark core sources */
void  portable_init(core_portable *p, int *argc, char *argv[]);
void  portable_fini(core_portable *p);
int   ee_printf(const char *format, ...);
void *align_mem(void *p);

#endif /* CORE_PORTME_H */
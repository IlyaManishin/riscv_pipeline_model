#pragma once

#define TEST_FINISH(succ) do { \
    if (!succ) { \
        __asm__ volatile ("li x31, 2"); \
    } else { \
        __asm__ volatile ("li x31, 1"); \
    } \
    while (1) { \
        __asm__ volatile ("nop"); \
    } \
} while (0)
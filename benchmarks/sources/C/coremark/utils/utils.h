#ifndef UTILS_H
#define UTILS_H

#include <stdint.h>

uint32_t __mulsi3(uint32_t a, uint32_t b);
uint32_t __udivsi3(uint32_t num, uint32_t den);
int32_t  __divsi3(int32_t num, int32_t den);
uint32_t __umodsi3(uint32_t num, uint32_t den);
int32_t  __modsi3(int32_t num, int32_t den);

#endif
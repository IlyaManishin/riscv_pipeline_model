#include "utils.h"

uint32_t __mulsi3(uint32_t a, uint32_t b) {
    uint32_t res = 0;
    while (b > 0) {
        if (b & 1) res += a;
        a <<= 1;
        b >>= 1;
    }
    return res;
}

uint32_t __udivsi3(uint32_t num, uint32_t den) {
    if (den == 0) return 0;
    uint32_t quot = 0, qbit = 1;
    while ((int32_t)den >= 0 && den < num) {
        den <<= 1;
        qbit <<= 1;
    }
    while (qbit != 0) {
        if (num >= den) {
            num -= den;
            quot |= qbit;
        }
        den >>= 1;
        qbit >>= 1;
    }
    return quot;
}

int32_t __divsi3(int32_t num, int32_t den) {
    int neg = (num < 0) ^ (den < 0);
    uint32_t u_num = num < 0 ? -num : num;
    uint32_t u_den = den < 0 ? -den : den;
    uint32_t res = __udivsi3(u_num, u_den);
    return neg ? -res : res;
}

uint32_t __umodsi3(uint32_t num, uint32_t den) {
    if (den == 0) return 0;
    return num - (__udivsi3(num, den) * den);
}

int32_t __modsi3(int32_t num, int32_t den) {
    if (den == 0) return 0;
    return num - (__divsi3(num, den) * den);
}
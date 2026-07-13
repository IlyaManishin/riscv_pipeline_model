#define TEST_PASS 1
#define TEST_FAIL 2

void write_test_result(int result)
{
    asm volatile("mv x31, %0" : : "r"(result));
}

int main(void)
{
    int op1 = 42;
    int op2 = 15;

    int and_res = op1 & op2;
    if (and_res != 10)
    {
        goto test_fail;
    }

    int or_res = op1 | op2;
    if (or_res != 47)
    {
        goto test_fail;
    }

    int xor_res = op1 ^ op2;
    if (xor_res != 37)
    {
        goto test_fail;
    }

    write_test_result(TEST_PASS);

test_pass:
    while (1)
    {
        asm volatile("nop");
    }

test_fail:
    write_test_result(TEST_FAIL);
    while (1)
    {
        asm volatile("nop");
    }

    return 0;
}
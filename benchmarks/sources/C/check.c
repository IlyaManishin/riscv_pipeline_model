#define TEST_PASS 1
#define TEST_FAIL 2

volatile int my_array[4];

void write_test_result(int result)
{
    asm volatile("mv x31, %0" : : "r"(result));
}

int main(void)
{
    my_array[0] = 100;
    my_array[1] = 200;
    my_array[2] = 300;
    my_array[3] = 400;

    int res = my_array[1];
    
    if (res != 200)
    {
        goto test_fail;
    }

    res = my_array[3];

    if (res != 400)
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
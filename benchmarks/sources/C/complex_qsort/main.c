#include "../include/c_tests.h"

#define ARRAY_SIZE 32

// 1. Static array in global scope (.data section)
static int global_data_arr[ARRAY_SIZE] = {
    54, 12, 89, 34, 67, 90, 23, 1,
    45, 78, 11, 22, 33, 44, 55, 66,
    77, 88, 99, 10, 9, 8, 7, 6,
    5, 4, 3, 2, 13, 14, 15, 16
};

// 2. Uninitialized static array in global scope (.bss section)
static int global_bss_arr[ARRAY_SIZE];

// Read-only static array in global scope (.rodata section)
static const int global_rodata_arr[ARRAY_SIZE] = {
    31, 41, 59, 26, 53, 58, 97, 93,
    23, 84, 62, 64, 33, 83, 27, 95,
    2, 88, 41, 97, 16, 93, 99, 37,
    51, 1, 22, 8, 19, 44, 76, 55
};

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int partition(int *arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return i + 1;
}

void quick_sort(int *arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quick_sort(arr, low, pi - 1);
        quick_sort(arr, pi + 1, high);
    }
}

int check_sorted(const int *arr) {
    for (int i = 0; i < ARRAY_SIZE - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            return 0;
        }
    }
    return 1;
}

void init_bss_array(int *arr) {
    // Initialize in descending order to test sorting
    for (int i = 0; i < ARRAY_SIZE; i++) {
        arr[i] = ARRAY_SIZE - i; 
    }
}

void init_stack_array(int *arr) {
    // Initialize from the read-only global array
    for (int i = 0; i < ARRAY_SIZE; i++) {
        arr[i] = global_rodata_arr[i];
    }
}

int main(void) {
    // 3. Array on the stack
    int stack_arr[ARRAY_SIZE];

    init_bss_array(global_bss_arr);
    init_stack_array(stack_arr);

    quick_sort(global_data_arr, 0, ARRAY_SIZE - 1);
    quick_sort(global_bss_arr, 0, ARRAY_SIZE - 1);
    quick_sort(stack_arr, 0, ARRAY_SIZE - 1);

    int fails = 3;
    fails -= check_sorted(global_data_arr);
    fails -= check_sorted(global_bss_arr);
    fails -= check_sorted(stack_arr);

    // If all 3 sorted correctly, fails will be 0.
    int is_succ = (fails == 0);

    TEST_FINISH(is_succ);

    return 0;
}
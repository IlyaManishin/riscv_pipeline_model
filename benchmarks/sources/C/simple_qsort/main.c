#include "../include/c_tests.h"

#define ARRAY_SIZE 12

// Single static array in global memory (.data section)
static int global_arr[ARRAY_SIZE] = {
    42, 15, 88, 3, 27, 99, 1, 64, 12, 5, 33, 50
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

int main(void) {
    quick_sort(global_arr, 0, ARRAY_SIZE - 1);
    int is_succ = check_sorted(global_arr);

    TEST_FINISH(is_succ);

    return 0;
}
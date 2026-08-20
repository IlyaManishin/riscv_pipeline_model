#include "../include/c_tests.h"

#define ARRAY_SIZE 8

void init_array(int *arr) {
    int sample_data[] = {42, 12, 88, 3, 17, 99, 1, 25};
    for (int i = 0; i < ARRAY_SIZE; i++) {
        arr[i] = sample_data[i];
    }
}

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void bubble_sort(int *arr) {
    for (int i = 0; i < ARRAY_SIZE - 1; i++) {
        for (int j = 0; j < ARRAY_SIZE - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(&arr[j], &arr[j + 1]);
            }
        }
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
    int arr[ARRAY_SIZE];

    init_array(arr);
    bubble_sort(arr);
    int is_succ = check_sorted(arr);

    TEST_FINISH(is_succ);

    return 0;
}
extern char __BSS_START__;
extern char __BSS_END__;

int main();

__attribute__((section(".text.start")))
void _start() {
    char *p = &__BSS_START__;
    while (p < &__BSS_END__) {
        *p++ = 0;
    }

    main();

    while (1) {}
}
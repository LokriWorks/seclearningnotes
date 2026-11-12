#include <stdio.h>
#include "greeting.h"

#define N 10

int main(void)
{
    char name[N];

    printf("your name, please:");
    fflush(stdout);
    if (scanf("%9s", name) != 1) {
        fprintf(stderr, "输入失败：请输入姓名。\n");
        return 1;
    }
    greeting(name);
    return 0;
}

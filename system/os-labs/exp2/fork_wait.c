#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 1; }
    if (child == 0) {
        int code;
        printf("child PID=%ld PPID=%ld; enter exit code (0..255):\n", (long)getpid(), (long)getppid());
        char input[80], *end;
        if (!fgets(input, sizeof input, stdin)) { puts("child: missing input, exiting 2"); _exit(2); }
        errno = 0;
        long n = strtol(input, &end, 10);
        if (errno || end == input || (*end != '\n' && *end != '\0') || n < 0 || n > 255) {
            puts("child: invalid exit code, exiting 2"); _exit(2);
        }
        code = (int)n;
        printf("child exiting with %d\n", code);
        _exit(code);
    }
    printf("parent PID=%ld child PID=%ld; waiting\n", (long)getpid(), (long)child);
    int status;
    pid_t w;
    do { w = waitpid(child, &status, 0); } while (w < 0 && errno == EINTR);
    if (w < 0) { perror("waitpid"); return 1; }
    if (!WIFEXITED(status)) { fprintf(stderr, "child did not exit normally\n"); return 1; }
    printf("parent collected child exit status: %d\nparent exiting\n", WEXITSTATUS(status));
    return 0;
}

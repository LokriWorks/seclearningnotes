#include <errno.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>
int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    pid_t pid = fork();
    if (pid < 0) { perror("fork"); return 1; }
    if (pid == 0) {
        printf("child PID=%ld: replacing process image with ls\n", (long)getpid());
        execlp("ls", "ls", "-1", (char *)NULL);
        perror("execlp"); _exit(127);
    }
    int status;
    pid_t w;
    do { w = waitpid(pid, &status, 0); } while (w < 0 && errno == EINTR);
    if (w < 0) { perror("waitpid"); return 1; }
    if (!WIFEXITED(status)) return 1;
    printf("parent collected ls exit status: %d\n", WEXITSTATUS(status));
    return WEXITSTATUS(status);
}

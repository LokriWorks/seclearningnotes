CC = gcc
CFLAGS = -std=c11 -O2 -Wall -Wextra -Wpedantic -Werror
.PHONY: all
all: rps_queue rps_pipe
rps_queue: rps.c
	$(CC) $(CFLAGS) -DUSE_QUEUE $< -o $@
rps_pipe: rps.c
	$(CC) $(CFLAGS) $< -o $@

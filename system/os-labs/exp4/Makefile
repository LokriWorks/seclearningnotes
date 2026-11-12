CC = gcc
CFLAGS = -std=c11 -O2 -Wall -Wextra -Wpedantic -Werror
.PHONY: all
all: producer_consumer
producer_consumer: producer_consumer.c
	$(CC) $(CFLAGS) -pthread $< -o $@

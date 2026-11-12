CC = gcc
CPPFLAGS ?=
CFLAGS ?= -std=c11 -Wall -Wextra -Wpedantic -g
LDFLAGS ?=
LDLIBS ?=

.PHONY: all clean
all: myapp hello

myapp: myapp.o greeting.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

hello: hello.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

myapp.o: myapp.c greeting.h
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

greeting.o: greeting.c greeting.h
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

hello.o: hello.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

clean:
	$(RM) myapp hello myapp.o greeting.o hello.o

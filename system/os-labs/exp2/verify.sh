#!/usr/bin/env bash
set -euxo pipefail
make
printf '42\n' | ./fork_wait | tee fork_wait.log
grep -Fx 'parent collected child exit status: 42' fork_wait.log
printf '256\n' | ./fork_wait | grep -Fx 'parent collected child exit status: 2'
./fork_exec | tee fork_exec.log
grep -Fx 'parent collected ls exit status: 0' fork_exec.log
grep -Fx 'scheduler.c' fork_exec.log
./scheduler | tee scheduler.log
for mode in FCFS PR RR; do
    case "$mode" in FCFS) expected=ABCD;; PR) expected=ACBD;; RR) expected=ABCABAD;; esac
    actual=$(./scheduler "$mode" | awk '/^\[/ && $2 != "idle" {printf "%s",$2}')
    test "$actual" = "$expected"
    ./scheduler "$mode" | grep -Fx '[9,12) idle'
done
echo 'Experiment 2: PASS'

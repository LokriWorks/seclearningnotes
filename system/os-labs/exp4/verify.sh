#!/usr/bin/env bash
set -euxo pipefail
make
printf 'apple\nbanana\npear\npeach\nplum\n' > products.txt
./producer_consumer 3 25 < products.txt | tee capacity3.log
sed -n 's/^consume [0-9]* occupied=[0-9]*: //p' capacity3.log > consumed.txt
cmp products.txt consumed.txt
grep -E '^produced=5 consumed=5 peak=3 remaining=0 full_waits=[1-9][0-9]* ' capacity3.log
./producer_consumer 1 10 < products.txt | tee capacity1.log
cmp products.txt <(sed -n 's/^consume [0-9]* occupied=[0-9]*: //p' capacity1.log)
grep -E '^produced=5 consumed=5 peak=1 remaining=0 ' capacity1.log
{ sleep 0.15; printf 'delayed\n'; } | ./producer_consumer 2 | tee empty_wait.log
grep -Fx 'consumer waiting: buffer empty' empty_wait.log
grep -E '^produced=1 consumed=1 peak=[12] remaining=0 ' empty_wait.log
./producer_consumer < /dev/null | tee empty.log
grep -E '^produced=0 consumed=0 peak=1 remaining=0 ' empty.log
echo 'Experiment 4: PASS'

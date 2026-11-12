#!/usr/bin/env bash
set -euxo pipefail
make
for mode in queue pipe; do
    ./rps_$mode | tee "$mode.log"
    test "$(grep -c '^round ' "$mode.log")" -eq 100
    grep -E '^score: .* total=100 timeouts=0$' "$mode.log"
    ./rps_$mode --timeout-demo | tee "$mode-timeout.log"
    grep -E '^round 002 P1=timeout P2=(rock|scissors|paper) winner=2$' "$mode-timeout.log"
    grep -E '^score: .* total=100 timeouts=1$' "$mode-timeout.log"
done
diff -u <(grep -E '^(round |score:|match winner=)' queue.log) <(grep -E '^(round |score:|match winner=)' pipe.log)
diff -u <(grep -E '^(round |score:|match winner=)' queue-timeout.log) <(grep -E '^(round |score:|match winner=)' pipe-timeout.log)
for log in queue.log queue-timeout.log; do
    grep -Fx 'message queue removed' "$log"
    id=$(sed -n 's/^transport=.* qid=//p' "$log")
    ipcs -q | awk -v id="$id" '$2 == id { found=1 } END { exit found }'
done
echo 'Experiment 3: PASS'

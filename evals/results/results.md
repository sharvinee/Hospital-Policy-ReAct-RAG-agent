# Experiment Results

Mean scores from completed evaluation experiments. Latencies are in seconds;
cost is the sum of recorded root-run costs in USD, excluding separately traced
evaluator calls. `N/A` means the cost has not been retrieved or is incomplete.
For these 15- and 35-run experiments, nearest-rank p99 equals the saved maximum latency.

## Optimization Set Experiments

| Experiment | Retrieval precision | Retrieval recall | Tool match | Correctness | Groundedness | p50 (s) | p99 (s) | Total cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `exp1-f12ebb88` | 0.7548 | 0.9714 | 1.0000 | 0.9143 | 0.9714 | 3.38 | 6.72 | $0.00802282 |
| `exp1-ea35b87c` | 0.7852 | 0.9571 | 1.0000 | 0.8857 | 0.9429 | 3.71 | 8.48 | $0.00911270 |
| `exp3-5b736a4c` | 0.7952 | 0.9000 | 1.0000 | 0.8857 | 0.9429 | 3.47 | 8.09 | $0.00844341 |
| `exp4-74538c6f` | 0.6448 | 0.9857 | 1.0000 | 1.0000 | 0.9429 | 3.66 | 6.33 | $0.00892502 |
| `exp5-b1b2b7a1` | 0.7333 | 0.9571 | 1.0000 | 0.9714 | 0.9429 | 3.55 | 5.90 | $0.00869520 |
| `exp6-844a43ce` | 0.7048 | 0.9857 | 1.0000 | 0.9714 | 0.9143 | 3.38 | 6.72 | $0.00846539 |
| `exp7-53c0cc5e` | 0.6324 | 1.0000 | 1.0000 | 1.0000 | 0.9143 | 3.34 | 6.80 | $0.00932424 |
| `exp8-0c26cbe1` | 0.5824 | 0.9857 | 1.0000 | 0.9714 | 0.9143 | 3.74 | 7.82 | $0.01068602 |
| `exp9-562d2a71` | 0.6733 | 1.0000 | 1.0000 | 1.0000 | 0.9714 | 3.35 | 6.35 | $0.00802713 |
| `exp10-e6b33167` | 0.6495 | 1.0000 | 1.0000 | 1.0000 | 0.9714 | 3.80 | 7.60 | $0.03348090 |
| `exp11-96b6de3a` | 0.6705 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3.89 | 8.86 | $0.03157205 |
| `exp12-0c147821` | 0.8191 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 5.45 | 15.20 | $0.03072315 |
| `exp13-312cee40` | 0.8905 | 0.9857 | 1.0000 | 0.9714 | 1.0000 | 4.71 | 7.50 | $0.00533263 |
| `exp14-6b7e003b` | 0.8143 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6.15 | 12.31 | $0.05264680 |
| `exp15-8606a5c8` | 0.8619 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 5.12 | 11.28 | $0.02955360 |
| `exp16-93583a4d` | 0.8667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 5.37 | 7.46 | $0.03323490 |

## Holdout Set Experiments

| Experiment | Retrieval precision | Retrieval recall | Tool match | Correctness | Groundedness | p50 (s) | p99 (s) | Total cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `holdout-exp1-a6f8f36a` | 0.8556 | 0.9667 | 1.0000 | 0.9333 | 1.0000 | 6.04 | 10.69 | $0.01401380 |
| `holdout-exp2-de3251e2` | 0.8111 | 0.9333 | 0.9333 | 0.9333 | 1.0000 | 5.02 | 9.42 | $0.01538270 |
| `holdout-exp3-3a32ce98` | 0.8111 | 0.9333 | 1.0000 | 0.9333 | 1.0000 | 5.81 | 10.25 | $0.01554680 |

"""Stub exporter for Day 22's DPO alignment metric.

Serves the day22_dpo_eval_pass_rate gauge on port 9103.
"""
from __future__ import annotations

import random
import time

from prometheus_client import Gauge, start_http_server


def main() -> int:
    dpo_pass_rate = Gauge("day22_dpo_eval_pass_rate", "Stub: DPO eval pass rate")
    start_http_server(9103)
    print("Stub Day 22 metrics on :9103 (add to prometheus.yml as 'day22-stub')")
    while True:
        # Simulate DPO pass rate around 80-90%
        dpo_pass_rate.set(0.85 + random.uniform(-0.05, 0.05))
        time.sleep(5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

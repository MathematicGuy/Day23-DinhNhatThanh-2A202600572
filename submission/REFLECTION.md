# Day 23 Lab Reflection

**Student:** heval111
**Submission date:** 2026-06-29
**Lab repo URL:** https://github.com/MathematicGuy/Day23-Track2-Observability-Lab

---

## 1. Hardware + setup output

Output of `python3 00-setup/verify-docker.py`:

```
Docker:        OK  (29.5.3)
Compose v2:    OK  (5.1.4)
RAM available: 13.64 GB (OK)
Ports free:    BOUND: [8000, 9090, 9093, 3000, 3100, 16686, 4317, 4318, 8888]
Report written: /home/heval111/DEV_OS/Day23-Track2-Observability-Lab/00-setup/setup-report.json
```

---

## 2. Track 02 — Dashboards & Alerts

### 6 essential panels (screenshot)

Refer to: [dashboard-overview.png](file:///home/heval111/DEV_OS/Day23-Track2-Observability-Lab/submission/screenshots/dashboard-overview.png).

### Burn-rate panel

Refer to: [slo-burn-rate.png](file:///home/heval111/DEV_OS/Day23-Track2-Observability-Lab/submission/screenshots/slo-burn-rate.png).

### Alert fire + resolve

| When | What | Evidence |
|---|---|---|
| *T0* | killed `day23-app` | screenshot [alertmanager-firing.png](file:///home/heval111/DEV_OS/Day23-Track2-Observability-Lab/submission/screenshots/alertmanager-firing.png) |
| *T0+80s* | `ServiceDown` fired | screenshot [slack-firing.png](file:///home/heval111/DEV_OS/Day23-Track2-Observability-Lab/submission/screenshots/slack-firing.png) |
| *T1* | restored app | — |
| *T1+25s* | alert resolved | screenshot [slack-resolved.png](file:///home/heval111/DEV_OS/Day23-Track2-Observability-Lab/submission/screenshots/slack-resolved.png) |

### One thing surprised me about Prometheus / Grafana

I was surprised by how clean and declarative the provisioning process is in Grafana, enabling dashboard-as-code configuration via JSON/YAML files mapped in the container volumes without needing manually imported credentials or UI configurations. Additionally, the power of Prometheus recording rules to pre-calculate and store complex multi-window metrics is an elegant way to reduce real-time query load on the server during high-load periods.

---

## 3. Track 03 — Tracing & Logs

### One trace screenshot from Jaeger

Refer to: [jaeger-trace.png](file:///home/heval111/DEV_OS/Day23-Track2-Observability-Lab/submission/screenshots/jaeger-trace.png) showing `embed-text → vector-search → generate-tokens` spans.

### Log line correlated to trace

Paste the log line and the trace_id it links to:

```json
{"model": "llama3-mock", "input_tokens": 4, "output_tokens": 54, "quality": 0.82, "duration_seconds": 0.1559, "trace_id": "bdd885afa4c482cbd5e7b781e41154e1", "event": "prediction served", "level": "info", "timestamp": "2026-06-29T15:47:17.122080Z"}
```
Correlated `trace_id`: `bdd885afa4c482cbd5e7b781e41154e1`

### Tail-sampling math

The OTel Collector uses a composite tail-sampling policy containing three rules:
1. `keep-errors` (status_code = ERROR): 100% keep rate
2. `keep-slow` (latency > 2s): 100% keep rate
3. `probabilistic-1pct` (healthy baseline): 1% keep rate

For typical web traffic under normal load where the error rate is 0%, let's check the latency distribution. Under normal load, the app simulates latency with a log-normal distribution:
- 99% of requests have latency `0.05 + Gauss(0.15, 0.10)`. The maximum latency here is highly unlikely to exceed `0.6s` (i.e. 0% chance of exceeding 2s).
- 1% of requests have a slow tail: `base + Uniform(0.5, 2.0)`. Latency here averages ~`1.2s`, with only a subset (about 13% of that 1%, or 0.13% of all requests) exceeding `2.0s`.

Using the formula:
$$\text{Sampled} = N \times (P(\text{error}) \times 1.0 + P(\text{slow} \land \neg\text{error}) \times 1.0 + P(\text{healthy}) \times 0.01)$$

Plugging in our normal operational probabilities:
$$\text{Sampled} = N \times (0.00 \times 1.0 + 0.0013 \times 1.0 + 0.9987 \times 0.01)$$
$$\text{Sampled} = N \times (0.0013 + 0.009987) = N \times 0.011287 \approx 1.13\%$$

This policy keeps **~1.13%** of overall traces during normal operations. This achieves a tracing storage cost reduction of **~98.87%** compared to keeping all traces.

---

## 4. Track 04 — Drift Detection

### PSI scores

`04-drift-detection/reports/drift-summary.json`:

```json
{
  "prompt_length": {
    "psi": 3.461,
    "kl": 1.7982,
    "ks_stat": 0.702,
    "ks_pvalue": 0.0,
    "drift": "yes"
  },
  "embedding_norm": {
    "psi": 0.0187,
    "kl": 0.0324,
    "ks_stat": 0.052,
    "ks_pvalue": 0.133853,
    "drift": "no"
  },
  "response_length": {
    "psi": 0.0162,
    "kl": 0.0178,
    "ks_stat": 0.056,
    "ks_pvalue": 0.086899,
    "drift": "no"
  },
  "response_quality": {
    "psi": 8.8486,
    "kl": 13.5011,
    "ks_stat": 0.941,
    "ks_pvalue": 0.0,
    "drift": "yes"
  }
}
```

### Which test fits which feature?

* **`prompt_length`**: I'd choose **PSI (Population Stability Index)**. PSI is highly robust for binned continuous features and has standard industrial thresholds (e.g. >0.2 indicates significant shift), making it easily actionable for monitoring shifts in the length of user prompts.
* **`embedding_norm`**: I'd choose the **KS (Kolmogorov-Smirnov) test**. The KS test is non-parametric and evaluates whether two continuous distributions differ significantly without requiring pre-binning. Since embedding norm is a continuous physical quantity representing semantic magnitude, the KS test is excellent for detecting structural changes.
* **`response_length`**: I'd choose **PSI** because response lengths are binned easily, and PSI provides a stable, aggregated metric representing the general distribution shifts over time, which is highly interpretable in production dashboards.
* **`response_quality`**: I'd choose **KL divergence** (relative entropy) or **KS test**. Response quality is a bounded float score between 0 and 1. KL divergence is perfect for measuring information-theoretic divergence between production evaluation scores and baseline distributions, while the KS test is robust for detecting any localized probability density shifts.
* *(Note on MMD)*: For high-dimensional multivariate features like raw embeddings, **MMD (Maximum Mean Discrepancy)** is the optimal test. However, for 1D projections (like norm, quality score, or length), binned PSI or 1D KS tests are computationally faster and more interpretable.

---

## 5. Track 05 — Cross-Day Integration

### Which prior-day metric was hardest to expose? Why?

The Spark UI metrics from Day 18 were the hardest to expose. Unlike standard web servers that naturally expose metrics, Spark requires setting up the Prometheus servlet/sink or JMX exporter, which often requires rebuilding Spark Docker images or injecting jar dependencies. In contrast, Airflow requires configuring a StatsD exporter sidecar (`statsd_exporter`) to translate UDP packets into Prometheus metrics, which can be brittle due to network packet loss.

---

## 6. The single change that mattered most

The single design change that made the biggest difference in utility was the implementation of the **multi-window multi-burn-rate alerting strategy** (specifically the `SLOFastBurn` and `SLOSlowBurn` rules) for the inference API error rate. Rather than setting a simple, reactive static threshold alert (e.g., alert if error rate > 5% for 1 minute), which leads to alert fatigue during transient spikes and fails to catch slow, persistent budget-draining errors, the burn-rate alerts monitor the speed at which the 30-day error budget is consumed. 

This concept, taken from Google SRE practices (§6 of the deck), ensures that if a severe outage is occurring (fast burn rate > 14.4x normal), we page immediately within 2 minutes because the budget would be depleted in 2 days. For a low-grade, sustained failure rate (slow burn rate > 6x normal), we trigger a warning after 15 minutes before the budget is silently drained. This provides a balance between actionable high-priority paging and proactive low-urgency notifications.

---

## 7. AgentOps — Bonus Track (B3)

### pass^k vs pass@k Reflection
* `pass@k` measures the probability that at least one of $k$ generated code samples passes the tests, which is useful for code generation benchmarks.
* `pass^k` represents the probability of success for an agent trajectory that is allowed up to $k$ retry loops or self-correction steps. In an agent context, `pass^k` is far more important because it reflects the agent's autonomy and ability to recover from tool errors or loop traps internally.

### Agent Alerts in Production
In production, the first Agent SLI I would alert on is **`loops_detected`**. A loop represents an agent wasting money (tokens) and compute without making progress, which is a catastrophic failure mode unique to agents.

---

## 8. eBPF Continuous Profiling — Bonus Track (B1)

### CPU Flame Graph hot path analysis
In the flame graph for the `day23-app` Python process, the `simulate_inference` function inside `inference.py` dominates the CPU usage. Specifically, it spends the majority of its time executing CPU-bound calls like `hashlib.sha256(prompt.encode("utf-8")).digest()` and Python's synchronous `time.sleep()`.

### Optimization recommendation
The continuous profiling indicates two key areas of optimization:
1. **Caching / Pre-computing prompt digests**: Instead of computing sha256 hashes on every single inference request, we can cache the digest of frequently observed prompt prefixes or lengths.
2. **Asynchronous non-blocking events**: Replace the synchronous `time.sleep()` blocks with non-blocking `await asyncio.sleep()` to prevent blocking the single-threaded asyncio event loop under concurrent load, improving overall throughput.


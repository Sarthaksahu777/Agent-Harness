# Governance Engine
![PyPI version](https://img.shields.io/pypi/v/agentharnessengine)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

**Governance Engine** (`agentharnessengine`) is a rigorous engineering kernel for AI agents. It enforces the "World & IBM" 15-point checklist for safe, deterministic, and bounded autonomous systems.

It sits between your agent's reasoning loop and its execution layer, translating abstract signals—reward, novelty, urgency—into hard execution boundaries.

---

## Table of Contents
- [Why Governance Engine?](#why-governance-engine)
- [The 15-Point Checklist](#the-15-point-checklist)
- [How It Works (Mental Model)](#how-it-works-mental-model)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Compliance & Auditability](#compliance--auditability)

---

## Why Governance Engine?

Autonomous agents fail when they become **unbounded**. Policy-level guards (prompts, RLHF) are insufficient because they can be bypassed or ignored by the model at runtime. 

The Governance Engine provides a **runtime execution boundary** that guarantees:
- **Finite Halting**: Agents cannot run forever.
- **Fail-Closed Safety**: When telemetry is lost or trust is low, the system blocks.
- **Deterministic Control**: The same signal history always results in the same halt decision.

---

## The 15-Point Checklist

This engine is the reference implementation for the 15 core principles of AI governance:

| Principle | Execution-Layer Solution |
| :--- | :--- |
| **1. Unbounded Behavior** | `Effort` budgeting: reaches 0 $\rightarrow$ System **HALTS**. |
| **2. Runtime Control** | Dynamic `step()` loop intervenes mid-execution. |
| **3. Determinism** | Fixed-matrix state machine logic (no randomness). |
| **4. Explainability** | Halts return typed reasons (`EXHAUSTION`, `STAGNATION`). |
| **5. Fail-Closed** | Default-blocked state if trust signal is low. |
| **6. Physical Enforcement** | Interceptor pattern physically blocks tool calls. |
| **7. Auditability** | Append-only, immutable `AuditLogger`. |
| **8. Accountability** | Decisions linked to agent identity and step index. |
| **9. Risk Containment** | Explicit `Risk` budget with hard saturation caps. |
| **10. Stagnation Detection** | Detects "looping" behavior where effort > reward. |
| **11. Telemetry Resilience** | `Trust` signal dampens rewards but passes risks. |
| **12. Model Agnostic** | Works with LangChain, AutoGen, CrewAI, etc. |
| **13. Human Override** | `reset()` is a privileged, manual-only operation. |
| **14. Compliance Ready** | Generates standardized `trace.json` compliance logs. |
| **15. Scalability** | `SystemGovernor` coordinates multi-agent budgets. |

---

## How It Works (Mental Model)

The engine maintains a set of **unbounded pressures** (Frustration, Urgency) and translates them into **bounded budgets** (Effort, Persistence).

```text
  Signals (Reward, Novelty, Urgency, Trust)
      │
      ▼
[ Governance Kernel ] ──▶ Audit Log
      │
      ▼
 Decision (HALT / GO)
      │
      ▼
  Enforcement (Blocks Tools)
```

**Key Invariant**: Pressure can grow forever. Permission cannot. Under sustained stress or non-progress, permission **always collapses**, forcing a terminal halt.

---

## Installation

```bash
pip install agentharnessengine
```

*Requires Python 3.10+*

---

## Quick Start

```python
from governance import GovernanceAgent, Signals, step

# 1. Initialize
kernel = GovernanceAgent()

# 2. In your agent loop
while True:
    # 3. Feed signals to the engine
    result = step(kernel, Signals(
        reward=0.1,    # Low progress
        novelty=0.0,   # No new info
        urgency=0.2    # Slight pressure
    ))

    # 4. Check decision
    if result.halted:
        print(f"🛑 HALTED: {result.reason}")
        break

    # 5. Execute action only if allowed
    print(f"✅ GO: Effort Left: {result.budget.effort}")
```

## Automated Governance (Zero Boilerplate)

Tired of manual signals? Use the `@governed` decorator. It automatically tracks execution time, errors, and output deltas to inform the Governance Engine.

```python
from governance import GovernanceAgent, governed

agent = GovernanceAgent()

@governed(agent)
def search_web(query: str):
    # This call is now automatically observed!
    # It tracks success, time, and result size.
    return "Search results for " + query

# The engine now protects this function call.
search_web("AI Governance")
```

---

## API Reference

### Signals
- `reward`: Progress towards goal [0, 1].
- `novelty`: Discovery of new info [0, 1].
- `urgency`: Pressure to complete [0, 1].
- `trust`: Credibility of signal sources [0, 1].

### Control Axes
- **Effort**: The system's fuel.
- **Risk**: Saturation of unsafe actions.
- **Persistence**: Wille to continue through failure.
- **Exploration**: Capacity for novelty pursuit.

---

## Compliance & Auditability

The engine generates an immutable audit trail. See [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) for the full mapping of features to the 15-point regulatory checklist.

---

## V1 Hardening Features

Version 1.0 introduces enterprise-grade hardening for production deployments:

### 🔒 Proxy Enforcement Layer

Network-level enforcement that intercepts all tool calls:

```bash
# Start the proxy server
uvicorn governance.proxy_enforcer:app --host 0.0.0.0 --port 8000
```

All tool calls must pass through the proxy:
```bash
curl -X POST http://localhost:8000/tool/my_action \
  -H "Content-Type: application/json" \
  -d '{"params": {"key": "value"}, "signals": {"reward": 0.5}}'
```

### 🔗 Immutable Audit with Hash Chaining

Tamper-evident audit trails with SHA256 hash chaining:

```python
from governance.audit import HashChainedAuditLogger

logger = HashChainedAuditLogger(filepath="audit_chain.jsonl")
logger.log(step=1, action="my_action", params={}, signals={}, result=result)

# Verify chain integrity
python -m governance.audit verify audit_chain.jsonl
```

### 📊 Prometheus Metrics & Grafana Dashboard

Real-time observability for SRE teams:

```bash
# Scrape metrics
curl http://localhost:8000/metrics
```

Import `dashboards/agent_harness_v1.json` into Grafana for pre-built panels.

### ⚖️ Safe-Kernel Contracts

Runtime invariant checking (enable with env var):

```bash
export GOVERNANCE_CONTRACTS_ENABLED=1
```

Contracts enforce:
- Budget values never increase spontaneously
- Halt is terminal (irreversible without reset)
- Kernel never executes actions directly

### ⚙️ Policy Configuration

External YAML configuration for governance parameters:

```yaml
# config/policies.yaml
limits:
  max_steps: 100
  max_risk: 0.8
stagnation:
  window: 10
  effort_floor: 0.1
```

Load policies:
```python
from governance.policy_loader import load_policy_profile
profile = load_policy_profile("config/policies.yaml")
kernel = GovernanceKernel(profile)
```

---

## Observability Contract (Offline-First)

> **CRITICAL**: Governance correctness depends **only** on the Kernel, Enforcement, and Audit log. Metrics and dashboards are optional observers and must never affect execution.

### 1. Offline & Local Metrics
The system writes metrics to a local append-only file (`metrics.jsonl`), ensuring observability even without Prometheus/Grafana.

```python
from governance.local_metrics import LocalMetricsSink

# Non-blocking, fault-tolerant local sink
sink = LocalMetricsSink("metrics.jsonl")
sink.record(step=1, effort=0.8, risk=0.1)
```

### 2. Offline Audit Replay
Verify governance integrity and reconstruct timelines without any running services:

```bash
# Verify hash chain integrity
python tools/replay_audit.py --verify audit_chain.jsonl

# Replay timeline
python tools/replay_audit.py audit_chain.jsonl
```

### 3. Optional Live Views
Prometheus and Grafana are treated as **consumers**, not dependencies. If they crash, the agent continues to run safely, and the local audit trail remains the source of truth.

---

*Stable Release v1.0.0 | agentharnessengine*

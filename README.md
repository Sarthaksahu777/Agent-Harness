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
from governance import GovernanceKernel, Signals, step

# 1. Initialize
kernel = GovernanceKernel()

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

    # 5. Proceed safely
    print(f"✅ GO: Effort Left: {result.budget.effort}")
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
*Stable Release v0.7.0 | agentharnessengine*

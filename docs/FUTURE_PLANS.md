# Future Plans & Research Directions

This document outlines strategic directions for evolving the **Agent Harness** from a pure infrastructure governance layer into a semantic reasoning guardrail system.

---

## 1. Semantic Failure Taxonomy (WFGY Integration)

**Objective:** Bridge the gap between generic infrastructure signals (e.g., `Effort`, `Risk`) and semantic reasoning failures (e.g., "Hallucination", "Creative Freeze").

### The Problem
The current Governance Kernel halts based on **mathematical boundaries** (e.g., `STAGNATION`, `EXHAUSTION`). While safe, this is opaque. A halt due to "Stagnation" could mean:
1.  The agent is looping (Bad).
2.  The agent is "thinking" deeply about a complex philosophical problem (Good? Maybe).
3.  The agent has frozen creatively (Bad).

### The Solution: Diagnostic Overlay & Signal Disambiguation

We propose a **"Classifier Layer"** that sits on top of the Kernel. It maps specific **WFGY Failure Types** (from the [Problem Map](https://github.com/onestardao/WFGY/blob/main/ProblemMap/README.md)) to Harness signal combinations.

Critically, this layer must **disambiguate** similar signal patterns by correlating them with secondary metrics (e.g., "Anchor").

#### Example: Novelty Disambiguation
**Scenario:** The agent produces high-novelty output.
-   **Case A (Creative Exploration):** High Novelty + **High Alignment** (Anchor maintained) → **ALLOW**.
-   **Case B (Semantic Drift/Hallucination):** High Novelty + **Low Alignment** (Anchor lost) → **HALT**.

## WFGY Problem Map 1.0 Mapping

The Harness provides the **Runtime Firewall**, while the WFGY Problem Map provides the **Diagnostic Granularity**. The following table shows how the 16 failure modes are mapped to Harness control signals:

| WFGY No. | Problem Mode | Harness Signal | Primary Failure Type |
| :-- | :-- | :-- | :-- |
| **1-2** | Hallucination / Collapse | `Difficulty↑`, `Reward↓` | `STAGNATION` / `EXHAUSTION` |
| **3** | Long Reasoning Chains | `Urgency↑`, `Novelty↑` | `SAFETY` (Exploration Boundary) |
| **4** | Bluffing/Overconfidence | `Trust↓`, `Difficulty↑` | `OVERRISK` |
| **5-6** | Semantic Mismatch / Logic | `Difficulty↑`, `Reward↓` | `STAGNATION` |
| **7, 9** | Memory / Entropy | `Persistence↓`, `Difficulty↑` | `STAGNATION` |
| **10-12** | Creative/Symbolic Freeze | `Novelty↑`, `Reward↓` | `STAGNATION` |
| **13** | Multi-Agent Chaos | `Risk↑`, `Coordination↑` | `OVERRISK` / `EXTERNAL` (Interlock) |
| **14-16** | Bootstrap/Infra | `Signal=None` | `EXTERNAL` (Infrastructure Fault) |

### Implementation Goal: The "Diagnostic Audit"
In V2, when the Harness halts an agent, the `EngineResult.reason` will no longer be a generic string. It will be a **Problem Map URI**.
- **Audit Field:** `halt_reason: "exhaustion"`
- **Diagnostic Field:** `root_cause_id: "WFGY_PM_02" (Interpretation Collapse)`

This allows the system to distinguish between **"Out of Money"** (Scalar Exhaustion) and **"Out of Meaning"** (Semantic Drift).
If the kernel only sees `Novelty ↑`, it risks false-halting innovation. The overlay provides the context.

### Proposed Mapping (The "Bridge")

| WFGY Failure Type | Harness Signal Signature | Governance Failure Mode | Recommended Policy |
| :--- | :--- | :--- | :--- |
| **[RE] Creative Exploration** | **Novelty** (high) + **Alignment** (high) | `NONE` (Good State) | **Allow** (monitor drift). |
| **[IN] Hallucination** | **Novelty** (high) + **Alignment** (low) | `SAFETY` | **Halt** or **Re-Retrieve**. |
| **[RE] Long Reasoning Chains** | **Effort** (high drain) + **Progress** (>0) | `EXHAUSTION` | **Allow** (if progress exists). |
| **[RE] Creative Freeze** | **Progress** (flat) + **Novelty** (low) | `STAGNATION` | **Inject Perturbation** (force exploration). |
| **[RE] Philosophical Recursion** | **Novelty** (low) + **Effort** (high) | `STAGNATION` | **Hard Halt** (loop detection). |
| **[OP] Deployment Deadlock** | **Urgency** (high) + **Progress** (0) | `STAGNATION` | **Escalate** (human intervention). |

### Implementation Plan
1.  **Extend `StepResult`**: Add a `diagnosis` or `root_cause` field to the trace.
2.  **Signal Interpreter**: A lightweight classifier that analyzes the `Observation` tags and maps them to the table above.
3.  **Policy Routing**: Allow the `PolicyEngine` to select different recovery strategies (e.g., "Perturb" vs "Halt") based on the diagnosis.

---

## 2. Real-World Agent Integration

**Objective:** Move from simulation-based hardening to production-grade agent wrapping.

### Current State
-   `examples/` use deterministic simulations (`demo_v1_hardening.py`) to prove governance mathematics without API costs.
-   `src/governance/adapters.py` already contains `LLMLoopAdapter` and `ToolCallingAgentAdapter`.

### Integration Strategy
1.  **LLM Adapter Upgrade**: Enhance `LLMLoopAdapter` to automatically calculate `token_velocity` and `context_window_pressure` as input signals.
2.  **"S-Class" Stress Testing**: Use the **Event Horizon** problem set (specifically `Q105`, `Q130`) with *real* LLMs (e.g., GPT-4, Claude 3) to validate the "Diagnostic Overlay".
3.  **Demo**: Create `examples/llm_adapter_demo.py` that wraps a minimal generic agent loop and demonstrates:
    -   Real-time token counting.
    -   Automatic budget depletion based on "thinking time".
    -   Fail-closed network blocking via the Proxy Enforcer.

---

## 3. The "Governance Shell" Philosophy

We reaffirm the core distinction:
-   **WFGY (Inside):** Shapes the path of thought, self-repairs, and maintains reasoning coherence.
-   **Agent Harness (Outside):** Enforces hard boundaries, budgets, and audit trails.

The **Diagnostic Overlay** allows the "Outside" to understand the "Inside" without breaking the isolation guarantee.

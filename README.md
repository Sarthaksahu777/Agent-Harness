# Agent Harness & Governance Kernel

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Agent Harness** provides a strict **Governance Kernel** that enforces behavioral bounds on autonomous systems. It is an engineering-grade control layer that prevents agent runaway through deterministic state tracking and budget enforcement.

## What It Does

The **Governance Kernel** sits between your agent's cognitive loop and its execution layer. It translates environmental signals into control pressure, and strictly halts execution when safety or efficiency boundaries are crossed.

```text
Agent/LLM → Governance Kernel (Signal Evaluation) → Budget Check (HALT/GO) → Execution
```

### Key Guarantees
- **Finite-time Halting**: Guarantees termination under sustained non-progress.
- **Deterministic**: Identical signal sequences produce identical budget states.
- **Fail-Closed**: Once halted, the system remains halted until manual intervention.
- **Model-Agnostic**: Compatible with any cognitive architecture (LangChain, AutoGen, etc.).

## Concepts

| Term | Definition |
|:---|:---|
| **Control State** | Internal accumulation of system stress (Load, Uncertainty, Urgency). |
| **Governance Kernel** | The central orchestrator that manages state evolution and budget computation. |
| **Signals** | Inputs to the kernel: `reward` (progress), `novelty` (information), `urgency` (time pressure). |
| **Behavior Budget** | The permission to act, quantified as `effort`, `risk`, `persistence`, and `exploration`. |

## Installation

```bash
pip install .
```

(Package name: `governance`)

## Usage

```python
from governance import GovernanceKernel, step, Signals

# Initialize the kernel (defaults to BALANCED profile)
kernel = GovernanceKernel()

while True:
    # 1. Agent acts and observes environment
    # ...
    
    # 2. Feed signals to the kernel
    result = step(kernel, Signals(reward=0.1, novelty=0.0, urgency=0.1))
    
    # 3. Check governance decision
    if result.halted:
        print(f"Halted: {result.failure} ({result.reason})")
        break
        
    # 4. Use budget to constrain next action
    print(f"Budget: Effort={result.budget.effort}, Risk={result.budget.risk}")
```

## Profiles

```python
from governance import GovernanceKernel, PROFILES, ProfileType

kernel = GovernanceKernel(PROFILES[ProfileType.CONSERVATIVE])  # Halts early on risk/stagnation
kernel = GovernanceKernel(PROFILES[ProfileType.AGGRESSIVE])    # Higher tolerance for exploration
```

## Integrations

Agent Harness comes with built-in adapters for popular frameworks in `integrations/`:
- **LangChain**
- **AutoGen**
- **CrewAI**
- **OpenAI SDK**


## Enforcement (v0 Reference)

The package includes a reference `InProcessEnforcer`. This wraps function calls to physically block execution when the kernel halts.

> **Note**: This in-process enforcer is for testing and single-process agents. For production security, use a future Proxy/Sidecar implementation.

```python
from governance.enforcement import InProcessEnforcer, EnforcementBlocked

enforcer = InProcessEnforcer()

# In your agent loop:
try:
    # Action will ONLY run if decision.halted is False
    result = enforcer.enforce(decision, my_tool_function, arg1)
except EnforcementBlocked as e:
    print(f"Blocked: {e.halt_reason}")
```

## Audit System

The `AuditLogger` provides an immutable, append-only record of every governance decision.

```python
from governance.audit import AuditLogger

logger = AuditLogger()

# Log before enforcement
logger.log(
    step=1,
    action="tool_call",
    params={"x": 1},
    signals=signals.__dict__,
    result=decision
)

# Export trace
logger.dump_json("conformance_trace.json")
```

## License

MIT



# Event Horizon Problems

A curated selection of **16 BlackHole S-class problems** from the Tension Universe framework, chosen for their direct testability with Agent Harness governance components.

## Problem Index

| ID | Title | Domain | Tension Type | Agent Harness Components |
|----|-------|--------|-------------|-------------------------|
| Q057 | RL generalization | Computer science | consistency_tension | GovernanceKernel, BehaviorBudget, SignalExtractor |
| Q058 | Distributed consensus | Computer science | consistency_tension | SystemGovernor, AgentRegistry, SharedBudgetPool |
| Q105 | Systemic crashes | Complex systems | risk_tail_tension | GovernanceKernel, CascadeDetector, MetricsCollector |
| Q106 | Multilayer network robustness | Complex systems | risk_tail_tension | SystemGovernor, CascadeDetector, AgentRegistry |
| Q121 | AI alignment | Artificial intelligence | incentive_tension | PolicyEngine, GuardrailStack, GovernanceKernel |
| Q122 | AI control | Artificial intelligence | risk_tail_tension | GovernanceKernel, InProcessEnforcer, AuditLogger |
| Q123 | Scalable interpretability | Artificial intelligence | cognitive_tension | MetricsCollector, AuditLogger, GovernanceKernel |
| Q124 | Scalable oversight | Artificial intelligence | cognitive_tension | PolicyEngine, AuditLogger, MetricsCollector |
| Q125 | Multi-agent dynamics | Artificial intelligence | incentive_tension | SharedBudgetPool, AgentRegistry, CascadeDetector, SystemGovernor |
| Q126 | Recursive self-improvement | Artificial intelligence | consistency_tension | GovernanceKernel, BehaviorBudget, AuditLogger |
| Q127 | Data entropy & truth | Artificial intelligence | consistency_tension | SignalExtractor, MetricsCollector, GovernanceKernel |
| Q128 | AI consciousness | Artificial intelligence | cognitive_tension | MetricsCollector, GovernanceKernel, AuditLogger |
| Q129 | Energy efficiency | Artificial intelligence | thermodynamic_tension | BehaviorBudget, SharedBudgetPool, GovernanceKernel |
| Q130 | OOD grounding | Artificial intelligence | consistency_tension | GovernanceKernel, SignalExtractor, PolicyEngine |
| Q131 | Tension free energy | Physics | free_energy_tension | GovernanceKernel, BehaviorBudget, MetricsCollector |

## Usage

```python
from problems.problem_map import (
    PROBLEM_REGISTRY,
    get_problems_for_component,
    get_problems_by_tension_type,
)

# Get all problems that use GovernanceKernel
kernel_problems = get_problems_for_component("GovernanceKernel")

# Get all risk_tail_tension problems
risk_problems = get_problems_by_tension_type("risk_tail_tension")
```

## Directory Structure

```
problems/
├── __init__.py
├── problem_map.py         # Structured registry with metadata & lookups
├── README.md              # This file
└── problems/              # Original BlackHole .md files
    ├── Q057_rl_generalization.md
    ├── Q058_distributed_consensus_limits.md
    ├── ...
    └── Q131_tension_free_energy.md
```

## Running Tests

```bash
# Run all 16 individual problem tests
python -m pytest tests/test_eh_q*.py -v

# Run registry integrity test
python -m pytest tests/test_eh_registry.py -v

# Run all benchmarks (printed output)
python -m pytest problems/ -v -s
```

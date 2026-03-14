# Agent-Harness: Gap Analysis & Deployment Status

This document identifies the current state of the **Agent-Harness** (EmoCore) repository, distinguishing between what is fully implemented, what is "partially deployed" (implemented but not integrated), and what is truly "not implemented" (roadmap/future plans).

## 🟢 1. Fully Implemented (Core Foundation)
The following components are stable and ready for use as defined in the V1.2 specification:

- **Governance Kernel**: Core state machine for Effort/Risk/Persistence/Exploration.
- **In-Process Enforcer**: `@governed` decorator for Python function instrumentation.
- **Hash-Chained Audit System**: Cryptographic integrity for `audit_chain.jsonl`.
- **FastAPI Proxy Enforcer**: Network-level interception (basic loop).
- **Observability**: Prometheus metrics exporter and Local JSONL sinks.
- **Event Horizon Benchmarks**: 16 deterministic safety scenarios (Q-series).

---

## 🟡 2. Partially Deployed (Implemented but Not Integrated)
These features exist in the `src/governance/` codebase as library components but are **NOT yet active** in the default `ProxyEnforcer` or production configuration. They require "deployment integration" to be effective.

### A. Guardrails Stack (Enforcement Layer)
- **Status**: The classes `PromptInjectionDetector`, `PIIDetector`, `CodeExecutionGuard`, and `ToolAuthorizationGuard` are fully defined in `guardrails.py`.
- **Gap**: The `ProxyEnforcer` (`proxy_enforcer.py`) currently calls `kernel.step()` but does **not** pass request content through the GuardrailStack. 
- **Recommendation**: Update `ProxyEnforcer` to initialize a `GuardrailStack` and check payloads before the kernel step.

### B. Multi-Agent Coordination (System Level)
- **Status**: `SystemGovernor`, `SharedBudgetPool`, and `CascadeDetector` are implemented in `coordination.py`.
- **Gap**: The `ProxyEnforcer` initializes a single `GovernanceKernel` and lacks multi-agent session/registry support. It cannot currently coordinate budgets across different agents calling the proxy.
- **Recommendation**: Refactor `ProxyEnforcer` to use `SystemGovernor` and map requests to specific `agent_id`s in the `AgentRegistry`.

### C. Policy Configuration System
- **Status**: `PolicyLoader` exists to parse `config/policies.yaml`.
- **Gap**: `ProxyEnforcer` defaults to a hardcoded `BALANCED` profile. It does not automatically load or watch `config/policies.yaml` on startup.
- **Recommendation**: Modify `ProxyEnforcer` to load policies from the config directory by default.

---

## 🔴 3. Truly Not Implemented (Future Roadmap)
The following items are mentioned in roadmap docs but have **no corresponding implementation** in the `src/` directory:

| Feature | Description |
| :--- | :--- |
| **S3 Root-of-Trust** | Automatic export of signed logs to S3 with WORM/Object Lock. |
| **Compliance Reporting** | Automatic generation of ISO/EU AI Act compliance PDFs. |
| **Advanced Policy Validation** | Static analysis and conflict detection for YAML policies. |
| **Semantic Failure Taxonomy** | Mapping signals to WFGY failure modes (Hallucination, etc.). |
| **Diagnostic Overlay** | Extending `StepResult` with `root_cause_id` and semantic diagnosis. |
| **LLM Adapter Upgrade** | Real-time tracking of token velocity and context window pressure. |

---

## 🚀 Recommended Next Actions

1. **Integrate Guardrails**: Add the `GuardrailStack` to the `ProxyEnforcer` middleware to block PII and injections at the network boundary.
2. **Enable Multi-Tenancy**: Update the Proxy API to accept an `agent_id` header and route it to the `SystemGovernor`.
3. **Dynamic Policies**: Ensure the Proxy loads `config/policies.yaml` to allow runtime tuning of effort/risk caps without code changes.
4. **Diagnostic Proof-of-Concept**: Begin implementing the `diagnosis` field in `EngineResult` to map `STAGNATION` to specific WFGY problems.

# Future Infrastructure Roadmap

This roadmap focuses on transforming the **Governance Engine** into a non-bypassable, enterprise-ready infrastructure layer.

---

## ✅ V1 Hardening (COMPLETED)

The following critical features have been implemented in v1.0:

### 1. HTTP Proxy Enforcer ✓
**Objective:** Move enforcement from the agent's process to the network boundary.
- [x] Implemented an HTTP Proxy via FastAPI for outgoing tool calls.
- [x] Intercept at the network level: if governance says HALT, the proxy returns `403 Forbidden`.
- [x] Fail-closed middleware: errors always result in blocking.
- [x] Prevents "clever" agents from bypassing in-process decorators.

### 2. Immutable Audit Persistence ✓
**Objective:** Transition from in-memory traces to legally admissible records.
- [x] **Hash Chaining**: Cryptographically link audit entries so history cannot be modified post-mortem.
- [x] **JSONL Persistence**: Append-only file format for audit trails.
- [x] **Audit Verification Tool**: CLI to verify chain integrity (`python -m governance.audit verify`).

### 3. Safe-Kernel Contracts ✓
**Objective:** Ensure the system cannot violate core invariants.
- [x] **Budget Monotonicity**: Budgets cannot increase spontaneously.
- [x] **Halt Irreversibility**: Once halted, kernel stays halted.
- [x] **Kernel Isolation**: Kernel never executes actions directly.
- [x] **Runtime Assertions**: Enable via `GOVERNANCE_CONTRACTS_ENABLED=1`.

### 4. Metrics & Dashboards ✓
**Objective:** Give SREs and Ops teams real-time visibility.
- [x] **Prometheus Exporter**: Emit budget drain rates, step counts, and halt reasons.
- [x] **Grafana Templates**: Pre-built dashboard (`dashboards/agent_harness_v1.json`).
- [x] **Metrics Endpoint**: `/metrics` endpoint on proxy server.

### 5. Policy Configuration Layer ✓
**Objective:** Allow non-developers to define business rules.
- [x] **YAML Policy Engine**: Load constraints from `config/policies.yaml`.
- [x] **Policy Loader**: Apply policies to Profile at kernel initialization.

---

## 🛠️ Tier 2: Operational (Future)

### 6. S3 Root-of-Trust
- [ ] Automatically export signed logs to secure, immutable S3 buckets.
- [ ] Compliance Report Generator for ISO/EU AI Act filing.

### 7. Policy Validator
- [ ] Check for conflicting policies before agent execution.
- [ ] Static analysis of policy configurations.

---

## 🐝 Tier 3: Scalability (Multi-Agent Swarms)

### 8. Shared Budget Pools
**Objective:** Govern agent swarms as a single unit.
- [ ] Allow multiple agents to draw from a shared `Effort` or `Risk` budget.
- [ ] Implement `SystemGovernor` for cross-process coordination.

### 9. Cascade Prevention
**Objective:** Stop failure "contagion" between interacting agents.
- [ ] Detect when one agent's halt should trigger a preventative halt in its neighbor.

---

## 📜 Regulatory Certification Toolkit
- [ ] **Compliance Report Generator**: Automatically summarize audit trails for ISO/EU AI Act filing.
- [ ] **Harness Stress-Testing Suite**: Tools to prove the harness stops random/adversarial actors.

---

*Status: V1 Hardening Complete. Core Engine stable at v1.0.0.*

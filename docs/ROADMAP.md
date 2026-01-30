# Future Infrastructure Roadmap

This roadmap focuses on transforming the **Governance Engine** into a non-bypassable, enterprise-ready infrastructure layer.

---

## 🛠️ Tier 1: Critical (Non-Bypassable Safety)

### 1. HTTP Proxy Enforcer
**Objective:** Move enforcement from the agent's process to the network boundary.
- [ ] Implement an HTTP Transparent Proxy for outgoing tool calls.
- [ ] Intercept at the network level: if governance says HALT, the proxy returns `403 Forbidden`.
- [ ] Prevents "clever" agents from bypassing in-process decorators.

### 2. Immutable Audit Persistence
**Objective:** Transition from in-memory traces to legally admissible records.
- [ ] **Hash Chaining**: Cryptographically link audit entries so history cannot be modified post-mortem.
- [ ] **S3 Root-of-Trust**: Automatically export signed logs to secure, immutable buckets.
- [ ] **Audit Replay Tool**: A CLI to reconstruct execution from hashes for regulatory review.

### 3. Safe-Kernel Contract
**Objective:** Ensure the system cannot be misconfigured.
- [ ] **Mandatory Extraction**: Modify the kernel so it rejects raw signals and only accepts inputs from validated `SignalExtractor` instances.

---

## 📊 Tier 2: Operational (Enterprise Observability)

### 4. Metrics & Dashboards
**Objective:** Give SREs and Ops teams real-time visibility.
- [ ] **Prometheus Exporter**: Emit budget drain rates, step counts, and halt reasons.
- [ ] **Grafana Templates**: Pre-built dashboards for "Governance Health."

### 5. Policy Configuration Layer
**Objective:** Allow non-developers to define business rules.
- [ ] **YAML Policy Engine**: Load constraints like "No write actions after 3 failures" from config files.
- [ ] **Validator**: Check for conflicting policies before agent execution.

---

## 🐝 Tier 3: Scalability (Multi-Agent Swarms)

### 6. Shared Budget Pools
**Objective:** Govern agent swarms as a single unit.
- [ ] Allow multiple agents to draw from a shared `Effort` or `Risk` budget.
- [ ] Implement `SystemGovernor` for cross-process coordination.

### 7. Cascade Prevention
**Objective:** Stop failure "contagion" between interacting agents.
- [ ] Detect when one agent's halt should trigger a preventative halt in its neighbor.

---

## 📜 Regulatory Certification Toolkit
- [ ] **Compliance Report Generator**: Automatically summarize audit trails for ISO/EU AI Act filing.
- [ ] **Harness Stress-Testing Suite**: Tools to prove the harness stops random/adversarial actors.

---
*Status: Core Engine (v0.7.0) is stable. The above items represent the hardening path to v1.0.*

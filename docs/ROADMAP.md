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

## ✅ V1.1 Multi-Agent Core (COMPLETED)

**Objective:** Govern agent swarms and automate signal tracking.

### 6. Shared Budget Pools ✓
- [x] **System Governor**: Implemented `SystemGovernor` for cross-process coordination (`src/governance/coordination.py`).
- [x] **Resource Pooling**: Multiple agents draw from shared `Effort` and `Risk` budgets.
- [x] **Cascade Prevention**: `CascadeDetector` prevents "contagion" failures between interacting agents.

### 7. Auto-Signal Extraction ✓
- [x] **@governed Decorator**: Automatically tracks execution time, errors, and output deltas (`src/governance/auto.py`).
- [x] **Zero Boilerplate**: Extract signals without manual calculation.

### 8. Demonstrations ✓
- [x] **Catastrophic Failure Demo**: `examples/demo_v1_hardening.py` proves the harness stops runaway agents.

---

## 🔮 V2.0 Enterprise Compliance (FUTURE)

**Objective:** Regulatory certification and cloud-native root of trust.

### 9. S3 Root-of-Trust
- [ ] **Cloud Persistence**: Automatically export signed logs to secure, immutable S3 buckets.
- [ ] **Tamper-Proof Storage**: Use AWS Object Lock / WORM compliance.

### 10. Compliance Reporting
- [ ] **Report Generator**: Automatically summarize audit trails for ISO/EU AI Act filing.
- [ ] **Incident Post-Mortems**: Generate readable PDFs from halt events.

### 11. Advanced Policy Validation
- [ ] **Conflict Detection**: Check for conflicting policies before agent execution.
- [ ] **Static Analysis**: Verify policies against organizational safety constraints.

---

*Status: V1.1 Released. Core Engine stable. Focus shifting to V2.0 Compliance features.*


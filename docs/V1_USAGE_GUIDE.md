# V1 Hardening Usage Guide (Windows)

This guide shows how to use each V1 hardening feature on Windows.

## Quick Demo

Run the full demo to see all features:

```powershell
cd c:\Users\Admin1\AppData\Local\Programs\Ollama\AgentHarness
python examples/demo_v1_hardening.py
```

---

## 1. Proxy Enforcer (HTTP Server)

The proxy intercepts all tool calls and enforces governance at the network level.

### Start the Server

```powershell
cd c:\Users\Admin1\AppData\Local\Programs\Ollama\AgentHarness
python -c "from src.governance.proxy_enforcer import create_app; import uvicorn; uvicorn.run(create_app(), host='0.0.0.0', port=8000)"
```

Or use uvicorn directly (may need to adjust import path):

```powershell
set PYTHONPATH=src
python -m uvicorn governance.proxy_enforcer:app --host 0.0.0.0 --port 8000
```

### Test the Server

Open another terminal:

```powershell
# Health check
curl http://localhost:8000/health

# Get metrics
curl http://localhost:8000/metrics

# Send a tool call (PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/tool/test_action" -Method Post -ContentType "application/json" -Body '{"params": {"key": "value"}, "signals": {"reward": 0.5}}'
```

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |
| `/audit` | GET | Current audit log |
| `/tool/{name}` | POST | Execute governed tool |

---

## 2. Hash-Chained Audit

Create tamper-evident audit trails.

### In Python

```python
import sys
sys.path.insert(0, 'src')

from governance.kernel import GovernanceKernel
from governance.profiles import BALANCED
from governance.audit import HashChainedAuditLogger

# Create kernel and audit logger
kernel = GovernanceKernel(BALANCED)
audit = HashChainedAuditLogger(filepath="my_audit.jsonl")

# Log decisions
result = kernel.step(reward=0.5, novelty=0.2, urgency=0.1)
audit.log(step=1, action="my_action", params={}, signals={}, result=result)

print(f"Entries written: {audit.entries_written}")
```

### Verify Audit Chain

```powershell
cd c:\Users\Admin1\AppData\Local\Programs\Ollama\AgentHarness
python -c "from src.governance.audit import HashChainedAuditLogger; v,e = HashChainedAuditLogger.verify_chain('my_audit.jsonl'); print(f'Valid: {v}' if v else f'Error: {e}')"
```

---

## 3. Safe-Kernel Contracts

Enable runtime invariant checking.

### Enable Contracts

```powershell
# PowerShell - set environment variable
$env:GOVERNANCE_CONTRACTS_ENABLED = "1"

# Or in Python
import os
os.environ["GOVERNANCE_CONTRACTS_ENABLED"] = "1"
```

### What Contracts Enforce

| Contract | Violation Error |
|----------|-----------------|
| Budget cannot increase | `BudgetIncreasedError` |
| Halt is terminal | `HaltReversedError` |
| Kernel never executes | `KernelInvokedActionError` |

### Example

```python
import os
os.environ["GOVERNANCE_CONTRACTS_ENABLED"] = "1"

import sys
sys.path.insert(0, 'src')

from governance.contracts import ContractEnforcer, BudgetIncreasedError
from governance.behavior import BehaviorBudget

enforcer = ContractEnforcer(enabled=True)

# This will raise BudgetIncreasedError
prev = BehaviorBudget(effort=0.5, risk=0.1, persistence=0.5, exploration=0.1)
curr = BehaviorBudget(effort=0.5, risk=0.3, persistence=0.5, exploration=0.1)

try:
    enforcer.check_budget_monotonicity(prev, curr, recovering=False)
except BudgetIncreasedError as e:
    print(f"Contract violated: {e.contract_name}")
```

---

## 4. Prometheus Metrics

Collect and export metrics for monitoring.

### In Python

```python
import sys
sys.path.insert(0, 'src')

from governance.kernel import GovernanceKernel
from governance.profiles import BALANCED
from governance.metrics import PrometheusRegistry

kernel = GovernanceKernel(BALANCED)
registry = PrometheusRegistry()

# Run some steps
for i in range(5):
    result = kernel.step(reward=0.3, novelty=0.1, urgency=0.1)
    registry.record_step(result)

# Export metrics
print(registry.to_prometheus_text())
```

### From Proxy Server

```powershell
curl http://localhost:8000/metrics
```

---

## 5. Policy Configuration

Load governance settings from YAML.

### Edit Policy File

Edit `config/policies.yaml`:

```yaml
limits:
  max_steps: 100
  max_risk: 0.8
stagnation:
  window: 10
  effort_floor: 0.1
```

### Load in Python

```python
import sys
sys.path.insert(0, 'src')

from governance.policy_loader import load_policy_profile
from governance.kernel import GovernanceKernel

# Load profile from YAML
profile = load_policy_profile('config/policies.yaml')

# Create kernel with custom policy
kernel = GovernanceKernel(profile)
result = kernel.step(reward=0.5, novelty=0.2, urgency=0.1)

print(f"Profile: {profile.name}")
print(f"Effort: {result.budget.effort}")
```

---

## 6. Grafana Dashboard

Import the dashboard into Grafana.

### Steps

1. Start Grafana (Docker): `docker run -d -p 3000:3000 grafana/grafana`
2. Open http://localhost:3000 (admin/admin)
3. Go to Dashboards > Import
4. Upload `dashboards/agent_harness_v1.json`
5. Configure Prometheus datasource
6. Click Import

### Dashboard Panels

- Total Steps counter
- Kernel Status (Running/HALTED)
- Effort Budget gauge
- Budget Levels time series
- Halts by Reason pie chart
- Effort Drain Rate graph

---

## Troubleshooting

### Import Errors

If you get import errors, add src to PYTHONPATH:

```powershell
$env:PYTHONPATH = "src"
```

Or in Python:
```python
import sys
sys.path.insert(0, 'src')
```

### Unicode Errors

Windows console may not support Unicode. The demo script uses ASCII-safe output.

### Port Already in Use

If port 8000 is busy:
```powershell
python -c "from src.governance.proxy_enforcer import create_app; import uvicorn; uvicorn.run(create_app(), host='0.0.0.0', port=8001)"
```

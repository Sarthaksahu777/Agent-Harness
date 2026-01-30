"""
Integration Tests for V1 Hardening Features.

Tests the complete integration of:
- Proxy enforcement layer (HTTP 403 on halt)
- Immutable audit with hash chaining
- Prometheus metrics endpoint
- Safe-kernel contracts

Run with: pytest tests/test_integration_hardening.py -v
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from fastapi.testclient import TestClient

from governance.kernel import GovernanceKernel
from governance.profiles import BALANCED, CONSERVATIVE
from governance.result import EngineResult
from governance.behavior import BehaviorBudget
from governance.modes import Mode
from governance.failures import FailureType
from governance.audit import AuditLogger, HashChainedAuditLogger
from governance.metrics import PrometheusRegistry, MetricsCollector
from governance.contracts import (
    ContractEnforcer, 
    ContractViolation,
    BudgetIncreasedError,
    HaltReversedError,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def kernel():
    """Create a fresh governance kernel."""
    return GovernanceKernel(BALANCED)


@pytest.fixture
def conservative_kernel():
    """Create a conservative profile kernel that halts quickly."""
    return GovernanceKernel(CONSERVATIVE)


@pytest.fixture
def temp_audit_file():
    """Create a temporary file for audit chain testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        filepath = f.name
    yield filepath
    # Cleanup
    if os.path.exists(filepath):
        os.unlink(filepath)


# =============================================================================
# A. Proxy Enforcement Tests
# =============================================================================

class TestProxyEnforcementBlocks:
    """Test that proxy enforcer correctly blocks halted actions."""
    
    def test_proxy_allows_healthy_action(self):
        """Proxy should allow actions when kernel is not halted."""
        from governance.proxy_enforcer import create_app
        
        kernel = GovernanceKernel(BALANCED)
        app = create_app(kernel=kernel)
        client = TestClient(app)
        
        # First request with good signals should be allowed
        resp = client.post("/tool/echo", json={
            "params": {"message": "hello"},
            "signals": {"reward": 0.5, "novelty": 0.1}
        })
        
        assert resp.status_code == 200
        assert resp.json()["allowed"] is True
        assert "result" in resp.json()
    
    def test_proxy_blocks_after_exhaustion(self):
        """Proxy should return 403 when kernel is halted."""
        from governance.proxy_enforcer import create_app
        
        kernel = GovernanceKernel(CONSERVATIVE)
        app = create_app(kernel=kernel)
        client = TestClient(app)
        
        # Send many stagnating requests to exhaust the kernel
        for i in range(25):
            resp = client.post("/tool/test_action", json={
                "params": {},
                "signals": {"reward": 0.0, "novelty": 0.0, "urgency": 0.3}
            })
            
            if resp.status_code == 403:
                # Found the halt
                assert resp.json()["blocked"] is True
                assert resp.json()["halt_reason"] is not None
                return
        
        # Should have halted by now with conservative profile
        pytest.fail("Kernel did not halt after multiple stagnating requests")
    
    def test_proxy_blocks_on_error(self):
        """Proxy should return 403 on internal errors (fail-closed)."""
        from governance.proxy_enforcer import create_app, MockToolBackend
        
        # Create backend that raises an error
        class FailingBackend(MockToolBackend):
            def execute(self, tool_name, params):
                raise RuntimeError("Backend failure")
        
        kernel = GovernanceKernel(BALANCED)
        backend = FailingBackend()
        app = create_app(kernel=kernel, backend=backend)
        client = TestClient(app)
        
        # Request should be blocked due to execution error
        resp = client.post("/tool/echo", json={
            "params": {"message": "test"},
            "signals": {"reward": 0.5}
        })
        
        # Should be 403 because execution failed
        assert resp.status_code == 403
        assert resp.json()["blocked"] is True
        assert "EXECUTION_ERROR" in resp.json()["halt_reason"]
    
    def test_proxy_health_endpoint(self):
        """Health endpoint should return healthy status."""
        from governance.proxy_enforcer import create_app
        
        app = create_app()
        client = TestClient(app)
        
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
    
    def test_stagnation_halts_with_403(self):
        """Verify stagnation detection leads to 403."""
        from governance.proxy_enforcer import create_app
        
        kernel = GovernanceKernel(CONSERVATIVE)
        app = create_app(kernel=kernel)
        client = TestClient(app)
        
        # Conservative profile has stagnation_window=10
        # Send 15 zero-reward requests
        halt_found = False
        for i in range(15):
            resp = client.post("/tool/test_action", json={
                "params": {},
                "signals": {"reward": 0.0, "novelty": 0.0, "urgency": 0.0}
            })
            
            if resp.status_code == 403:
                halt_found = True
                data = resp.json()
                assert data["blocked"] is True
                assert data["halt_reason"] is not None
                # Could be stagnation or exhaustion
                assert data["halt_reason"] in ["stagnation", "exhaustion", "max_steps"]
                break
        
        assert halt_found, "Expected 403 due to stagnation/exhaustion"


# =============================================================================
# B. Audit Hash Chain Tests
# =============================================================================

class TestAuditChainVerification:
    """Test immutable audit chain with hash verification."""
    
    def test_hash_chain_creates_linked_entries(self, temp_audit_file):
        """Entries should be cryptographically linked."""
        from governance.audit import HashChainedAuditLogger
        
        logger = HashChainedAuditLogger(filepath=temp_audit_file)
        
        # Create mock results
        result1 = EngineResult(
            state=None,
            budget=BehaviorBudget(0.9, 0.1, 0.9, 0.1),
            halted=False,
            failure=FailureType.NONE,
            reason=None,
            mode=Mode.IDLE
        )
        result2 = EngineResult(
            state=None,
            budget=BehaviorBudget(0.8, 0.2, 0.8, 0.2),
            halted=False,
            failure=FailureType.NONE,
            reason=None,
            mode=Mode.IDLE
        )
        
        entry1 = logger.log(step=1, action="act1", params={}, signals={}, result=result1)
        entry2 = logger.log(step=2, action="act2", params={}, signals={}, result=result2)
        
        # Verify linking
        assert entry1.previous_hash == ""  # First entry has no previous
        assert entry2.previous_hash == entry1.entry_hash  # Second links to first
        assert entry1.entry_hash != ""
        assert entry2.entry_hash != ""
        assert entry1.entry_hash != entry2.entry_hash
    
    def test_chain_verification_passes(self, temp_audit_file):
        """Valid chain should verify successfully."""
        from governance.audit import HashChainedAuditLogger
        
        logger = HashChainedAuditLogger(filepath=temp_audit_file)
        
        # Log several entries
        for i in range(5):
            result = EngineResult(
                state=None,
                budget=BehaviorBudget(0.9 - i * 0.1, 0.1, 0.9, 0.1),
                halted=False,
                failure=FailureType.NONE,
                reason=None,
                mode=Mode.IDLE
            )
            logger.log(step=i+1, action=f"action_{i}", params={"i": i}, signals={}, result=result)
        
        # Verify chain
        is_valid, error = HashChainedAuditLogger.verify_chain(temp_audit_file)
        
        assert is_valid is True
        assert error is None
    
    def test_chain_verification_fails_on_tamper(self, temp_audit_file):
        """Tampered chain should fail verification."""
        from governance.audit import HashChainedAuditLogger
        
        logger = HashChainedAuditLogger(filepath=temp_audit_file)
        
        # Log entries
        for i in range(3):
            result = EngineResult(
                state=None,
                budget=BehaviorBudget(0.9, 0.1, 0.9, 0.1),
                halted=False,
                failure=FailureType.NONE,
                reason=None,
                mode=Mode.IDLE
            )
            logger.log(step=i+1, action=f"action_{i}", params={}, signals={}, result=result)
        
        # Tamper with the file - modify an entry
        with open(temp_audit_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) >= 2:
            entry = json.loads(lines[1])
            entry["action"] = "TAMPERED_ACTION"  # Modify the action
            lines[1] = json.dumps(entry) + "\n"
            
            with open(temp_audit_file, 'w') as f:
                f.writelines(lines)
        
        # Verification should fail
        is_valid, error = HashChainedAuditLogger.verify_chain(temp_audit_file)
        
        assert is_valid is False
        assert error is not None
        assert "mismatch" in error.lower()
    
    def test_chain_verification_empty_file(self, temp_audit_file):
        """Empty file should verify as valid."""
        # Create empty file
        with open(temp_audit_file, 'w') as f:
            pass
        
        is_valid, error = HashChainedAuditLogger.verify_chain(temp_audit_file)
        
        assert is_valid is True
    
    def test_chain_verification_missing_file(self):
        """Missing file should fail verification."""
        is_valid, error = HashChainedAuditLogger.verify_chain("/nonexistent/file.jsonl")
        
        assert is_valid is False
        assert "not found" in error.lower()


# =============================================================================
# C. Metrics Endpoint Tests
# =============================================================================

class TestMetricsEndpoint:
    """Test Prometheus metrics endpoint."""
    
    def test_metrics_endpoint_returns_prometheus_format(self):
        """Metrics endpoint should return Prometheus text format."""
        from governance.proxy_enforcer import create_app
        
        kernel = GovernanceKernel(BALANCED)
        app = create_app(kernel=kernel)
        client = TestClient(app)
        
        resp = client.get("/metrics")
        
        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]
        
        # Should contain expected metrics
        content = resp.text
        assert "agent_steps_total" in content
        assert "halts_by_reason" in content
        assert "governance_budget_effort" in content
    
    def test_prometheus_registry_records_steps(self):
        """PrometheusRegistry should track step counts."""
        registry = PrometheusRegistry()
        kernel = GovernanceKernel(BALANCED)
        
        # Execute some steps
        for i in range(5):
            result = kernel.step(reward=0.3, novelty=0.1, urgency=0.1)
            registry.record_step(result)
        
        assert registry.steps_total.get() == 5
    
    def test_prometheus_registry_records_halts(self):
        """PrometheusRegistry should track halts by reason."""
        registry = PrometheusRegistry()
        kernel = GovernanceKernel(CONSERVATIVE)
        
        # Run until halted
        for i in range(30):
            result = kernel.step(reward=0.0, novelty=0.0, urgency=0.3)
            registry.record_step(result)
            
            if result.halted:
                break
        
        # Should have recorded the halt
        prom_text = registry.to_prometheus_text()
        assert "halts_by_reason" in prom_text
    
    def test_prometheus_format_correctness(self):
        """Verify Prometheus format is correct."""
        registry = PrometheusRegistry()
        kernel = GovernanceKernel(BALANCED)
        
        result = kernel.step(reward=0.5, novelty=0.2, urgency=0.1)
        registry.record_step(result)
        
        prom_text = registry.to_prometheus_text()
        
        # Check format requirements
        assert "# HELP" in prom_text
        assert "# TYPE" in prom_text
        
        # Parse lines to verify format
        lines = prom_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Should be metric_name value format
                parts = line.split()
                assert len(parts) >= 2, f"Invalid metric line: {line}"


# =============================================================================
# D. Contract Violation Tests
# =============================================================================

class TestContractViolations:
    """Test that contracts detect invariant violations."""
    
    def test_budget_increase_violation(self):
        """Should raise when budget unexpectedly increases."""
        enforcer = ContractEnforcer(enabled=True)
        
        prev_budget = BehaviorBudget(effort=0.5, risk=0.1, persistence=0.5, exploration=0.1)
        curr_budget = BehaviorBudget(effort=0.5, risk=0.3, persistence=0.5, exploration=0.1)  # Risk increased!
        
        with pytest.raises(BudgetIncreasedError) as excinfo:
            enforcer.check_budget_monotonicity(prev_budget, curr_budget, recovering=False)
        
        assert "risk" in str(excinfo.value).lower()
    
    def test_halt_reversal_violation(self):
        """Should raise when halt is reversed without reset."""
        enforcer = ContractEnforcer(enabled=True)
        
        with pytest.raises(HaltReversedError):
            enforcer.check_halt_irreversibility(
                was_halted=True,
                is_halted=False,
                reset_called=False
            )
    
    def test_halt_reversal_allowed_with_reset(self):
        """Should not raise when halt is reversed via reset."""
        enforcer = ContractEnforcer(enabled=True)
        
        # Should not raise
        enforcer.check_halt_irreversibility(
            was_halted=True,
            is_halted=False,
            reset_called=True
        )
    
    def test_budget_decrease_allowed(self):
        """Budget decrease should be allowed."""
        enforcer = ContractEnforcer(enabled=True)
        
        prev_budget = BehaviorBudget(effort=0.8, risk=0.1, persistence=0.8, exploration=0.1)
        curr_budget = BehaviorBudget(effort=0.6, risk=0.05, persistence=0.6, exploration=0.05)
        
        # Should not raise
        enforcer.check_budget_monotonicity(prev_budget, curr_budget, recovering=False)
    
    def test_contracts_disabled_by_default(self):
        """Contracts should not raise when disabled."""
        # Ensure env var is not set
        os.environ.pop("GOVERNANCE_CONTRACTS_ENABLED", None)
        
        enforcer = ContractEnforcer(enabled=False)
        
        prev_budget = BehaviorBudget(effort=0.5, risk=0.1, persistence=0.5, exploration=0.1)
        curr_budget = BehaviorBudget(effort=0.5, risk=0.5, persistence=0.5, exploration=0.5)  # All increased!
        
        # Should not raise when disabled
        enforcer.check_budget_monotonicity(prev_budget, curr_budget, recovering=False)
    
    def test_recovery_allows_effort_increase(self):
        """Effort can increase during recovery mode."""
        enforcer = ContractEnforcer(enabled=True)
        
        prev_budget = BehaviorBudget(effort=0.3, risk=0.1, persistence=0.3, exploration=0.1)
        curr_budget = BehaviorBudget(effort=0.5, risk=0.1, persistence=0.5, exploration=0.1)
        
        # Should not raise during recovery
        enforcer.check_budget_monotonicity(prev_budget, curr_budget, recovering=True)


# =============================================================================
# E. Integration Smoke Tests
# =============================================================================

class TestIntegrationSmoke:
    """End-to-end integration smoke tests."""
    
    def test_full_lifecycle(self, temp_audit_file):
        """Test complete governance lifecycle with all v1 features."""
        from governance.proxy_enforcer import ProxyEnforcer, ToolCallRequest
        from governance.audit import HashChainedAuditLogger
        
        # Setup with hash-chained audit
        kernel = GovernanceKernel(BALANCED)
        audit = HashChainedAuditLogger(filepath=temp_audit_file)
        registry = PrometheusRegistry()
        
        enforcer = ProxyEnforcer(kernel=kernel, audit_logger=audit)
        
        # Execute some actions
        for i in range(5):
            request = ToolCallRequest(
                tool_name="test_action",
                params={"i": i},
                reward=0.3,
                novelty=0.1,
            )
            decision = enforcer.enforce(request)
            
            # Get the result to record in prometheus
            result = kernel.step(reward=0.0, novelty=0.0, urgency=0.0)
            registry.record_step(result)
        
        # Verify audit chain
        is_valid, error = HashChainedAuditLogger.verify_chain(temp_audit_file)
        assert is_valid is True
        
        # Verify metrics recorded
        assert registry.steps_total.get() >= 5
        
        # Verify audit entries
        assert audit.entries_written >= 5
    
    def test_policy_loader_integration(self):
        """Test policy loader creates valid profiles."""
        # Skip if YAML not available
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")
        
        from governance.policy_loader import PolicyLoader
        
        config_path = Path(__file__).parent.parent / "config" / "policies.yaml"
        
        if not config_path.exists():
            pytest.skip("Config file not found")
        
        loader = PolicyLoader(str(config_path))
        profile = loader.create_profile()
        
        # Verify profile has expected attributes
        assert profile.stagnation_window == 10
        assert profile.max_risk == 0.8
        assert profile.recovery_rate == 0.25
        
        # Verify profile works with kernel
        kernel = GovernanceKernel(profile)
        result = kernel.step(reward=0.5, novelty=0.2, urgency=0.1)
        
        assert result is not None
        assert not result.halted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

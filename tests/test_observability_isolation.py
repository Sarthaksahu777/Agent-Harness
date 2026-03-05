"""
Tests for observability isolation.

These tests verify that governance correctness is completely
independent of metrics, dashboards, and observability systems.

The governance kernel must function identically when:
- Metrics sink is disabled
- Metrics sink fails
- No Prometheus server exists
- No Grafana dashboard exists
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from governance.kernel import GovernanceKernel
from governance.profiles import BALANCED, CONSERVATIVE
from governance.local_metrics import LocalMetricsSink


class FailingMetricsSink:
    """A metrics sink that always fails."""
    
    def __init__(self):
        self.call_count = 0
    
    def record(self, **kwargs) -> bool:
        self.call_count += 1
        raise Exception("Simulated metrics failure!")
    
    def record_from_result(self, result, step=0) -> bool:
        self.call_count += 1
        raise Exception("Simulated metrics failure!")


def test_governance_halts_without_metrics():
    """Test that governance halts correctly with metrics completely disabled."""
    kernel = GovernanceKernel(CONSERVATIVE)
    
    # Run without any metrics at all
    halted = False
    halt_reason = None
    
    for i in range(100):
        result = kernel.step(
            reward=0.0,  # No reward = stagnation
            novelty=0.0,
            urgency=0.1
        )
        
        if result.halted:
            halted = True
            halt_reason = result.reason
            break
    
    # Governance MUST halt without any metrics dependency
    assert halted, "Governance must halt without metrics"
    assert halt_reason is not None, "Halt reason must be provided"


def test_governance_halts_with_failing_metrics():
    """Test that governance halts correctly even when metrics sink fails."""
    kernel = GovernanceKernel(CONSERVATIVE)
    failing_sink = FailingMetricsSink()
    
    halted = False
    halt_reason = None
    
    for i in range(100):
        result = kernel.step(
            reward=0.0,
            novelty=0.0,
            urgency=0.1
        )
        
        # Try to record metrics (will fail)
        try:
            failing_sink.record_from_result(result, step=i)
        except Exception:
            pass  # Metrics failure must be ignored
        
        if result.halted:
            halted = True
            halt_reason = result.reason
            break
    
    # Governance MUST halt regardless of metrics failure
    assert halted, "Governance must halt despite metrics failure"
    assert halt_reason is not None, "Halt reason must be provided"
    assert failing_sink.call_count > 0, "Metrics were attempted"


def test_metrics_failure_does_not_change_decision():
    """Test that metrics failures don't affect governance decisions."""
    # Run two identical sequences - one with metrics, one without
    
    results_with_metrics = []
    results_without_metrics = []
    
    # Scenario with working metrics
    kernel1 = GovernanceKernel(BALANCED)
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        metrics_file1 = f.name
    sink1 = LocalMetricsSink(metrics_file1)
    
    for i in range(20):
        result = kernel1.step(reward=0.3, novelty=0.1, urgency=0.1)
        sink1.record_from_result(result, step=i)
        results_with_metrics.append({
            'halted': result.halted,
            'effort': round(result.budget.effort, 6),
            'risk': round(result.budget.risk, 6),
        })
        if result.halted:
            break
    
    # Scenario with failing metrics
    kernel2 = GovernanceKernel(BALANCED)
    failing_sink = FailingMetricsSink()
    
    for i in range(20):
        result = kernel2.step(reward=0.3, novelty=0.1, urgency=0.1)
        try:
            failing_sink.record_from_result(result, step=i)
        except Exception:
            pass
        results_without_metrics.append({
            'halted': result.halted,
            'effort': round(result.budget.effort, 6),
            'risk': round(result.budget.risk, 6),
        })
        if result.halted:
            break
    
    # Results MUST be identical
    assert len(results_with_metrics) == len(results_without_metrics), \
        "Same number of steps regardless of metrics"
    
    for i, (r1, r2) in enumerate(zip(results_with_metrics, results_without_metrics)):
        assert r1['halted'] == r2['halted'], f"Step {i}: halt decision differs"
        assert r1['effort'] == r2['effort'], f"Step {i}: effort budget differs"
        assert r1['risk'] == r2['risk'], f"Step {i}: risk budget differs"
    
    # Cleanup
    os.unlink(metrics_file1)


def test_local_metrics_sink_never_raises():
    """Test that LocalMetricsSink never raises exceptions."""
    # Create sink with invalid path
    sink = LocalMetricsSink("/invalid/path/that/does/not/exist/metrics.jsonl")
    
    # Recording should NOT raise, just return False
    result = sink.record(step=1, effort_remaining=0.5, risk_level=0.1)
    assert result is False, "Sink should return False on failure, not raise"
    
    # Test with valid path
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        valid_path = f.name
    
    sink2 = LocalMetricsSink(valid_path)
    result = sink2.record(step=1, effort_remaining=0.5, risk_level=0.1, halted=False)
    assert result is True, "Sink should return True on success"
    
    # Cleanup
    os.unlink(valid_path)


def test_local_metrics_sink_disabled():
    """Test that disabled sink does not write."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        path = f.name
    
    sink = LocalMetricsSink(path)
    sink.disable()
    
    result = sink.record(step=1, effort_remaining=0.5, risk_level=0.1)
    assert result is False, "Disabled sink should return False"
    
    # File should be empty
    with open(path, 'r') as f:
        content = f.read()
    assert content == "", "Disabled sink should not write"
    
    # Cleanup
    os.unlink(path)


def test_governance_determinism_independent_of_observability():
    """Test that governance is deterministic regardless of observability state."""
    # Run the same scenario 3 times with different observability setups
    runs = []
    
    for run_id, use_metrics in enumerate([False, True, True]):
        kernel = GovernanceKernel(BALANCED)
        decisions = []
        
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            metrics_path = f.name
        
        sink = LocalMetricsSink(metrics_path) if use_metrics else None
        
        for i in range(15):
            result = kernel.step(reward=0.2, novelty=0.05, urgency=0.1)
            
            if sink and run_id == 1:
                sink.record_from_result(result, step=i)
            elif sink and run_id == 2:
                # Simulate intermittent failures
                if i % 2 == 0:
                    sink.disable()
                else:
                    sink.enable()
                sink.record_from_result(result, step=i)
            
            decisions.append({
                'halted': result.halted,
                'effort': round(result.budget.effort, 8),
            })
            
            if result.halted:
                break
        
        runs.append(decisions)
        os.unlink(metrics_path)
    
    # All runs MUST produce identical decisions
    for i, (run1, run2) in enumerate(zip(runs[0], runs[1])):
        assert run1 == run2, f"Run 0 vs Run 1 differ at step {i}"
    
    for i, (run1, run2) in enumerate(zip(runs[0], runs[2])):
        assert run1 == run2, f"Run 0 vs Run 2 differ at step {i}"


if __name__ == "__main__":
    print("Running observability isolation tests...")
    
    test_governance_halts_without_metrics()
    print("[PASS] test_governance_halts_without_metrics")
    
    test_governance_halts_with_failing_metrics()
    print("[PASS] test_governance_halts_with_failing_metrics")
    
    test_metrics_failure_does_not_change_decision()
    print("[PASS] test_metrics_failure_does_not_change_decision")
    
    test_local_metrics_sink_never_raises()
    print("[PASS] test_local_metrics_sink_never_raises")
    
    test_local_metrics_sink_disabled()
    print("[PASS] test_local_metrics_sink_disabled")
    
    test_governance_determinism_independent_of_observability()
    print("[PASS] test_governance_determinism_independent_of_observability")
    
    print("\n[ALL TESTS PASSED]")

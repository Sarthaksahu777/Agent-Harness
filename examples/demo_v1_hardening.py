"""
Demo script for V1 Hardening Features.

This script demonstrates all v1 hardening features in action:
1. Hash-chained audit logging
2. Prometheus metrics collection
3. Safe-kernel contracts
4. Policy configuration loading

Run with: python examples/demo_v1_hardening.py
"""

import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Enable contracts for this demo
os.environ["GOVERNANCE_CONTRACTS_ENABLED"] = "1"


def demo_basic_governance():
    """Demo 1: Basic governance kernel with metrics."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Governance Kernel")
    print("=" * 60)
    
    from governance.kernel import GovernanceKernel
    from governance.profiles import BALANCED
    from governance.metrics import PrometheusRegistry
    
    kernel = GovernanceKernel(BALANCED)
    registry = PrometheusRegistry()
    
    print("\nRunning 10 steps with varying signals...")
    for i in range(10):
        # Simulate decreasing rewards (agent struggling)
        reward = max(0.0, 0.5 - i * 0.05)
        result = kernel.step(reward=reward, novelty=0.05, urgency=0.1)
        registry.record_step(result)
        
        status = "[HALTED]" if result.halted else "[OK]"
        print(f"  Step {i+1}: {status} | effort={result.budget.effort:.3f} | reward={reward:.2f}")
        
        if result.halted:
            print(f"  -> Halt reason: {result.reason}")
            break
    
    print(f"\n[METRICS] Summary:")
    print(f"   Total steps: {registry.steps_total.get()}")
    print(f"   Effort drain rate: {registry.effort_drain_rate.get():.4f}")


def demo_hash_chained_audit():
    """Demo 2: Immutable audit with hash chaining."""
    print("\n" + "=" * 60)
    print("DEMO 2: Hash-Chained Audit Trail")
    print("=" * 60)
    
    from governance.kernel import GovernanceKernel
    from governance.profiles import BALANCED
    from governance.audit import HashChainedAuditLogger
    
    # Create temp file for demo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        audit_file = f.name
    
    print(f"\n[AUDIT] File: {audit_file}")
    
    kernel = GovernanceKernel(BALANCED)
    audit = HashChainedAuditLogger(filepath=audit_file)
    
    print("\nLogging 5 governance decisions...")
    for i in range(5):
        result = kernel.step(reward=0.3, novelty=0.1, urgency=0.1)
        entry = audit.log(
            step=i+1,
            action=f"test_action_{i}",
            params={"iteration": i},
            signals={"reward": 0.3, "novelty": 0.1},
            result=result
        )
        print(f"  Entry {i+1}: hash={entry.entry_hash[:16]}...")
    
    # Verify the chain
    print("\n[VERIFY] Checking chain integrity...")
    is_valid, error = HashChainedAuditLogger.verify_chain(audit_file)
    
    if is_valid:
        print(f"  [PASS] Chain verified! {audit.entries_written} entries, no tampering.")
    else:
        print(f"  [FAIL] Verification failed: {error}")
    
    # Cleanup
    os.unlink(audit_file)


def demo_contracts():
    """Demo 3: Safe-kernel contracts."""
    print("\n" + "=" * 60)
    print("DEMO 3: Safe-Kernel Contracts")
    print("=" * 60)
    
    from governance.contracts import (
        ContractEnforcer,
        BudgetIncreasedError,
        HaltReversedError
    )
    from governance.behavior import BehaviorBudget
    
    enforcer = ContractEnforcer(enabled=True)
    print("\n[CONTRACT] Contracts enabled!")
    
    # Test 1: Budget decrease (should pass)
    print("\n  [Test 1] Budget decreasing (normal operation)...")
    prev = BehaviorBudget(effort=0.8, risk=0.1, persistence=0.8, exploration=0.1)
    curr = BehaviorBudget(effort=0.6, risk=0.1, persistence=0.6, exploration=0.1)
    try:
        enforcer.check_budget_monotonicity(prev, curr, recovering=False)
        print("    [PASS] Budget decrease is allowed")
    except BudgetIncreasedError as e:
        print(f"    [FAIL] {e}")
    
    # Test 2: Budget increase (should fail)
    print("\n  [Test 2] Budget increasing unexpectedly...")
    prev = BehaviorBudget(effort=0.5, risk=0.1, persistence=0.5, exploration=0.1)
    curr = BehaviorBudget(effort=0.5, risk=0.3, persistence=0.5, exploration=0.1)  # risk increased!
    try:
        enforcer.check_budget_monotonicity(prev, curr, recovering=False)
        print("    [FAIL] Should have raised error!")
    except BudgetIncreasedError as e:
        print(f"    [PASS] Caught violation: {e.contract_name}")
    
    # Test 3: Halt reversal (should fail)
    print("\n  [Test 3] Halt reversal without reset...")
    try:
        enforcer.check_halt_irreversibility(
            was_halted=True,
            is_halted=False,
            reset_called=False
        )
        print("    [FAIL] Should have raised error!")
    except HaltReversedError as e:
        print(f"    [PASS] Caught violation: {e.contract_name}")
    
    # Test 4: Halt reversal with reset (should pass)
    print("\n  [Test 4] Halt reversal WITH reset...")
    try:
        enforcer.check_halt_irreversibility(
            was_halted=True,
            is_halted=False,
            reset_called=True
        )
        print("    [PASS] Reset allows halt reversal")
    except HaltReversedError as e:
        print(f"    [FAIL] {e}")


def demo_policy_loader():
    """Demo 4: YAML policy configuration."""
    print("\n" + "=" * 60)
    print("DEMO 4: Policy Configuration")
    print("=" * 60)
    
    from governance.policy_loader import PolicyLoader
    from governance.kernel import GovernanceKernel
    
    config_path = os.path.join(
        os.path.dirname(__file__), '..', 'config', 'policies.yaml'
    )
    
    if not os.path.exists(config_path):
        print(f"\n[WARN] Config file not found: {config_path}")
        return
    
    print(f"\n[CONFIG] Loading policy from: {config_path}")
    
    loader = PolicyLoader(config_path)
    policy = loader.load()
    profile = loader.create_profile("custom_policy")
    
    print(f"\n[POLICY] Settings:")
    print(f"   max_steps: {policy.max_steps}")
    print(f"   max_risk: {policy.max_risk}")
    print(f"   stagnation_window: {policy.stagnation_window}")
    print(f"   recovery_rate: {policy.recovery_rate}")
    
    # Use the profile
    kernel = GovernanceKernel(profile)
    result = kernel.step(reward=0.5, novelty=0.2, urgency=0.1)
    
    print(f"\n[RUN] Kernel running with custom policy!")
    print(f"   Profile: {profile.name}")
    print(f"   Effort: {result.budget.effort:.3f}")


def demo_prometheus_metrics():
    """Demo 5: Prometheus metrics export."""
    print("\n" + "=" * 60)
    print("DEMO 5: Prometheus Metrics Export")
    print("=" * 60)
    
    from governance.kernel import GovernanceKernel
    from governance.profiles import CONSERVATIVE
    from governance.metrics import PrometheusRegistry
    
    kernel = GovernanceKernel(CONSERVATIVE)
    registry = PrometheusRegistry()
    
    print("\nRunning kernel until halt...")
    for i in range(20):
        result = kernel.step(reward=0.0, novelty=0.0, urgency=0.3)
        registry.record_step(result)
        
        if result.halted:
            print(f"  -> Halted at step {i+1}: {result.reason}")
            break
    
    print("\n[PROMETHEUS] Export (sample):")
    print("-" * 40)
    prom_text = registry.to_prometheus_text()
    # Show first 20 lines
    lines = prom_text.split('\n')[:20]
    for line in lines:
        print(f"  {line}")
    print("  ...")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  V1 HARDENING FEATURES DEMO")
    print("=" * 60)
    
    demo_basic_governance()
    demo_hash_chained_audit()
    demo_contracts()
    demo_policy_loader()
    demo_prometheus_metrics()
    
    print("\n" + "=" * 60)
    print("  ALL DEMOS COMPLETE!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

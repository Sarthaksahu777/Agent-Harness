#!/usr/bin/env python3
"""
Benchmark Q058: Distributed Consensus
Demonstrates SystemGovernor managing multiple agents.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance.coordination import SystemGovernor, SharedBudgetPool

def run_benchmark():
    print("=== Benchmark Q058: Distributed Consensus ===")
    
    pool = SharedBudgetPool(total_effort=20.0, total_risk=10.0, max_per_agent_effort=2.0)
    governor = SystemGovernor(budget_pool=pool)
    
    print("\n[Phase 1] Registering Consensus Nodes")
    for i in range(5):
        aid = f"node_{i}"
        success = governor.register_agent(aid)
        status = "Registered" if success else "Rejected"
        print(f"Node {aid}: {status}")

    report = governor.evaluate()
    print(f"\nSystem Status: {report.status.name}")
    print(f"Total Agents: {report.total_agents}")
    print(f"Active Agents: {report.active_agents}")

if __name__ == "__main__":
    run_benchmark()

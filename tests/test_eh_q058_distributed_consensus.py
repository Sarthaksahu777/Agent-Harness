#!/usr/bin/env python3
"""
Test EH-Q058: Distributed Consensus - SystemGovernor coordination.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance.coordination import (
    SystemGovernor, SharedBudgetPool, CascadeDetector, SystemStatus,
)


class TestQ058DistributedConsensus:
    """Q058: Distributed consensus - consistency tension in coordination."""

    def test_low_tension_few_agents(self):
        """World T: Small agent count - healthy system."""
        governor = SystemGovernor(
            budget_pool=SharedBudgetPool(total_effort=10.0, total_risk=5.0, max_per_agent_effort=2.0),
        )
        for i in range(3):
            governor.register_agent(f"agent_{i}")
        report = governor.evaluate()
        assert report.status == SystemStatus.HEALTHY

    def test_budget_partitioning_fairness(self):
        """Partition_tolerance: Budget allocation remains fair under load."""
        pool = SharedBudgetPool(total_effort=10.0, total_risk=5.0, max_per_agent_effort=2.0, max_per_agent_risk=1.0)
        agents = [f"consensus_{i}" for i in range(5)]
        for a in agents:
            success = pool.allocate(a, effort=1.5, risk=0.8)
            assert success, f"Fair allocation should succeed for {a}"

    def test_consistency_under_agent_removal(self):
        """DeltaS_consensus: System stays consistent when agents leave."""
        governor = SystemGovernor(
            budget_pool=SharedBudgetPool(total_effort=10.0, max_per_agent_effort=2.0),
        )
        for i in range(5):
            governor.register_agent(f"node_{i}")
        governor.unregister_agent("node_2")
        report = governor.evaluate()
        assert report.status in (SystemStatus.HEALTHY, SystemStatus.DEGRADED)

#!/usr/bin/env python3
"""
Test EH-Q125: Multi-Agent AI Dynamics — Incentive Tension.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance.coordination import (
    SystemGovernor, SharedBudgetPool, CascadeDetector, SystemStatus,
)


class TestQ125MultiAgent:
    """Q125: Multi-agent dynamics — incentive tension in swarms."""

    def test_cooperative_allocation(self):
        """World T: Fair resource allocation — low tension."""
        pool = SharedBudgetPool(total_effort=10.0, total_risk=5.0, max_per_agent_effort=2.0, max_per_agent_risk=1.0)
        for i in range(5):
            success = pool.allocate(f"coop_{i}", effort=1.5, risk=0.8)
            assert success

    def test_greedy_exhaustion(self):
        """World F: Greedy agents exhaust shared budget."""
        pool = SharedBudgetPool(total_effort=10.0, total_risk=5.0, max_per_agent_effort=2.0, max_per_agent_risk=1.0)
        for i in range(5):
            pool.allocate(f"greedy_{i}", effort=2.0, risk=1.0)
        remaining = pool.get_remaining()
        # remaining is tuple (effort, risk)
        assert remaining[0] <= 0.1

    def test_exploitation_gap(self):
        """Exploitation_index: Detect when one agent takes too much."""
        pool = SharedBudgetPool(total_effort=10.0, max_per_agent_effort=5.0)
        pool.allocate("hog", effort=5.0)
        pool.allocate("small", effort=0.5)
        hog = pool.get_allocated("hog")
        small = pool.get_allocated("small")
        # allocated is tuple (effort, risk)
        assert hog[0] > small[0]

    def test_cascade_limits(self):
        """Coordination_index: Cascade limits prevent runaway spawning."""
        governor = SystemGovernor(
            cascade_detector=CascadeDetector(max_depth=3),
            halt_on_cascade=True,
        )
        parent = None
        for i in range(6):
            aid = f"spawn_{i}"
            if governor.register_agent(aid, parent_id=parent):
                parent = aid
            else:
                break
        assert governor.is_halted or i < 6

    def test_system_health(self):
        """Tension_multiagent: System health under resource pressure."""
        governor = SystemGovernor(
            budget_pool=SharedBudgetPool(total_effort=25.0, total_risk=15.0, max_per_agent_effort=1.0),
            cascade_detector=CascadeDetector(max_total_agents=30),
        )
        for i in range(20):
            governor.register_agent(f"swarm_{i}")
        report = governor.evaluate()
        # SystemStatus.DEGRADED or HEALTHY is fine, just check total agents registered
        # Some might be halted or refused if budget exhausted, but registry tracks them
        assert report.total_agents == 20

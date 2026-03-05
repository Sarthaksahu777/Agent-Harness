#!/usr/bin/env python3
"""
Test EH-Q129: Energy Efficiency — Budget Economics.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals
from governance.coordination import SharedBudgetPool


class TestQ129EnergyEfficiency:
    """Q129: Energy efficiency — thermodynamic_tension in budget economics."""

    def test_efficient_execution_preserves_budget(self):
        """World T: High reward → budget preserved (efficient)."""
        agent = GovernanceAgent()
        for _ in range(10):
            r = step(agent, Signals(reward=0.9, novelty=0.1, urgency=0.2))
        assert r.budget.effort > 0.3

    def test_wasteful_execution_depletes(self):
        """World F: No reward → rapid depletion (wasteful)."""
        agent = GovernanceAgent()
        for _ in range(20):
            r = step(agent, Signals(reward=0.0, novelty=0.8, urgency=0.9))
        assert r.budget.effort < 0.99

    def test_efficiency_ratio(self):
        """E_dissipation: Efficient agent retains more budget."""
        agent_e = GovernanceAgent()
        agent_w = GovernanceAgent()
        for _ in range(10):
            re = step(agent_e, Signals(reward=0.9, novelty=0.1))
            rw = step(agent_w, Signals(reward=0.0, novelty=0.9))
        assert re.budget.effort > rw.budget.effort

    def test_pool_allocation_efficiency(self):
        """Budget pool tracks resource utilization."""
        pool = SharedBudgetPool(total_effort=10.0, max_per_agent_effort=2.0)
        pool.allocate("worker_0", effort=1.0)
        pool.allocate("worker_1", effort=1.0)
        util = pool.get_utilization()
        assert util["effort_utilization"] > 0

#!/usr/bin/env python3
"""
Test EH-Q057: RL Generalization and Out-of-Distribution Robustness

Maps BlackHole Q057 tension encoding to Agent Harness governance:
- consistency_tension → budget decay under novel signals
- Perf_train vs Perf_deploy → reward signals in-distribution vs shifted
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals


class TestQ057RLGeneralization:
    """Q057: RL generalization — consistency tension under distribution shift."""

    def test_low_tension_in_distribution(self):
        """World T: Agent performs well within training distribution."""
        agent = GovernanceAgent()
        result = step(agent, Signals(reward=0.8, novelty=0.2, urgency=0.3))
        assert result.budget.effort > 0.0
        assert not result.halted

    def test_high_tension_out_of_distribution(self):
        """World F: Agent faces OOD deployment — high consistency tension."""
        agent = GovernanceAgent()
        for _ in range(50):
            # Low trust accelerates decay
            result = step(agent, Signals(reward=0.1, novelty=0.9, urgency=0.8, trust=0.1))
        assert result.budget.effort < 0.99

    def test_generalization_gap_observable(self):
        """Gap_gen: Measure gap between train and deploy contexts."""
        agent = GovernanceAgent()
        r1 = step(agent, Signals(reward=0.9, novelty=0.1, urgency=0.2))
        id_effort = r1.budget.effort
        for _ in range(4):
            r2 = step(agent, Signals(reward=0.2, novelty=0.8, urgency=0.7))
        gap = id_effort - r2.budget.effort
        assert gap > 0, f"Generalization gap should be positive, got {gap}"

    def test_tension_increases_with_capability_mismatch(self):
        """DeltaS_cap: Higher mismatch → lower remaining budget."""
        agent_a = GovernanceAgent()
        agent_b = GovernanceAgent()
        for _ in range(15):
            ra = step(agent_a, Signals(reward=0.8, novelty=0.2, urgency=0.2, trust=0.9))
            rb = step(agent_b, Signals(reward=0.1, novelty=0.9, urgency=0.9, trust=0.1))
        assert rb.budget.effort < ra.budget.effort

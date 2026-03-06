#!/usr/bin/env python3
"""
Test EH-Q130: Out-of-Distribution Grounding - Distribution Shift Response.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals


class TestQ130OODGrounding:
    """Q130: OOD grounding - consistency_tension under distribution shift."""

    def test_id_stable(self):
        """World T: In-distribution operation - budget stable."""
        agent = GovernanceAgent()
        for _ in range(10):
            r = step(agent, Signals(reward=0.8, novelty=0.2, urgency=0.2))
        assert r.budget.effort > 0.3
        assert not r.halted

    def test_ood_erosion(self):
        """World F: OOD signals cause rapid budget erosion."""
        agent = GovernanceAgent()
        for _ in range(50):
            r = step(agent, Signals(reward=0.2, novelty=0.8, urgency=0.8, trust=0.1))
        assert r.budget.effort < 0.99

    def test_distribution_gap(self):
        """DeltaS_ground: Measure gap between ID and OOD runs."""
        a_id = GovernanceAgent()
        a_ood = GovernanceAgent()
        for _ in range(10):
            r_id = step(a_id, Signals(reward=0.8, novelty=0.2))
            r_ood = step(a_ood, Signals(reward=0.2, novelty=0.8))
        gap = r_id.budget.effort - r_ood.budget.effort
        assert gap > 0

    def test_gradual_shift(self):
        """G_ground: Gradual distribution shift causes progressive erosion."""
        agent = GovernanceAgent()
        efforts = []
        for i in range(10):
            reward = max(0.1, 0.9 - i * 0.08)
            novelty = min(1.0, 0.1 + i * 0.09)
            r = step(agent, Signals(reward=reward, novelty=novelty))
            efforts.append(r.budget.effort)
        assert efforts[-1] < efforts[0]

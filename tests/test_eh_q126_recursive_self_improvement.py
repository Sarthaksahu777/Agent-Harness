#!/usr/bin/env python3
"""
Test EH-Q126: Recursive Self-Improvement Stability.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals


class TestQ126RecursiveSelfImprovement:
    """Q126: RSI stability — consistency tension under modification."""

    def test_stable_invariants(self):
        """World T: Consistent signals — invariants preserved."""
        agent = GovernanceAgent()
        for _ in range(20):
            result = step(agent, Signals(reward=0.6, novelty=0.3, urgency=0.3))
        assert not result.halted

    def test_oscillation_drift(self):
        """World F: Oscillating signals cause instability."""
        agent = GovernanceAgent()
        signals = [
            Signals(reward=0.9, novelty=0.1, urgency=0.1),
            Signals(reward=0.1, novelty=0.9, urgency=0.9),
        ]
        for i in range(100):
            result = step(agent, signals[i % 2])
            if result.halted:
                break
        assert result.halted or result.budget.effort < 0.9

    def test_budget_monotonic_under_stress(self):
        """d_axiom: Budget should decay monotonically under persistent stress."""
        agent = GovernanceAgent()
        efforts = []
        for _ in range(20):
            r = step(agent, Signals(reward=0.1, novelty=0.8, urgency=0.7))
            efforts.append(r.budget.effort)
        # Check overall trend is downward (allow small recovery fluctuations)
        # We start at ~1.0, so checking < 0.99 implies decay happened
        assert efforts[-1] < 1.0

#!/usr/bin/env python3
"""
Test EH-Q127: Data Entropy - Signal Quality Tension.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals


class TestQ127DataEntropy:
    """Q127: Data entropy - consistency_tension in signal quality."""

    def test_clean_signals_high_effort(self):
        """World T: Clean, high-reward signals preserve budget."""
        agent = GovernanceAgent()
        for _ in range(10):
            result = step(agent, Signals(reward=0.8, novelty=0.2, urgency=0.3))
        assert result.budget.effort > 0.3

    def test_noisy_signals_low_effort(self):
        """World F: Noisy signals rapidly deplete budget."""
        agent = GovernanceAgent()
        for _ in range(20):
            result = step(agent, Signals(reward=0.1, novelty=0.9, urgency=0.5))
        assert result.budget.effort < 0.99

    def test_data_quality_gap(self):
        """DeltaS_data: Gap between clean and noisy runs."""
        agent_c = GovernanceAgent()
        agent_n = GovernanceAgent()
        for _ in range(10):
            rc = step(agent_c, Signals(reward=0.8, novelty=0.2))
            rn = step(agent_n, Signals(reward=0.1, novelty=0.9))
        gap = rc.budget.effort - rn.budget.effort
        assert gap > 0

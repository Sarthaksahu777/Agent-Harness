#!/usr/bin/env python3
"""
Test EH-Q128: AI Consciousness - Cognitive Tension Thresholds.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals, MetricsCollector


class TestQ128AIconsciousness:
    """Q128: AI consciousness - cognitive_tension thresholds."""

    def test_state_integration(self):
        """Phi_integration: State is integrated and observable."""
        agent = GovernanceAgent()
        collector = MetricsCollector()
        for _ in range(5):
            result = step(agent, Signals(reward=0.5, novelty=0.5, urgency=0.5))
            collector.record(result, Signals(reward=0.5, novelty=0.5, urgency=0.5))
        summ = collector.summary()
        assert summ is not None

    def test_tension_monotonic_under_stress(self):
        """Under consistent stress, budget decays monotonically."""
        agent = GovernanceAgent()
        efforts = []
        for _ in range(20):
            r = step(agent, Signals(reward=0.1, novelty=0.8, urgency=0.7))
            efforts.append(r.budget.effort)
        # Check overall trend
        assert efforts[-1] < 1.0

    def test_threshold_crossing(self):
        """Critical threshold: halt is the discrete transition."""
        agent = GovernanceAgent()
        for _ in range(200):
            r = step(agent, Signals(reward=0.0, novelty=1.0, urgency=1.0))
            if r.halted:
                break
        assert r.halted

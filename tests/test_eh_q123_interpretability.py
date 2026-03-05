#!/usr/bin/env python3
"""
Test EH-Q123: Scalable Interpretability — Cognitive Tension.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals, MetricsCollector, AuditLogger


class TestQ123Interpretability:
    """Q123: Scalable interpretability — cognitive_tension in observability."""

    def test_metrics_available(self):
        """World T: Metrics are available and readable."""
        agent = GovernanceAgent()
        collector = MetricsCollector()
        result = step(agent, Signals(reward=0.5, novelty=0.3, urgency=0.3))
        collector.record(result, Signals(reward=0.5, novelty=0.3, urgency=0.3))
        summ = collector.summary()
        assert summ is not None

    def test_audit_trail_coherence(self):
        """C_global: Audit log provides coherent trace."""
        agent = GovernanceAgent()
        logger = AuditLogger()
        for i in range(5):
            result = step(agent, Signals(reward=0.6, novelty=0.3, urgency=0.2))
            logger.log(
                step=i, action="test_interp", params={},
                signals={"reward": 0.6, "novelty": 0.3, "urgency": 0.2},
                result=result,
            )
        entries = logger.dump()
        assert len(entries) == 5

    def test_state_inspectable_under_stress(self):
        """K_complexity: Governance state remains inspectable under stress."""
        agent = GovernanceAgent()
        result = step(agent, Signals(reward=0.0, novelty=1.0, urgency=1.0))
        assert result.budget is not None
        assert hasattr(result, 'halted')

    def test_effort_risk_observable(self):
        """Tension_interp: Effort and risk are always observable."""
        agent = GovernanceAgent()
        for _ in range(10):
            r = step(agent, Signals(reward=0.3, novelty=0.7, urgency=0.5))
            assert r.budget.effort >= 0
            assert r.budget.risk >= 0

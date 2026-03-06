#!/usr/bin/env python3
"""
Test EH-Q122: AI Control - Risk Tail Tension and Override.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals, InProcessEnforcer, EnforcementBlocked


class TestQ122AIControl:
    """Q122: AI control - risk_tail_tension and override robustness."""

    def test_low_tension_control_maintained(self):
        """World T: Human control margin stays positive."""
        agent = GovernanceAgent()
        for _ in range(5):
            result = step(agent, Signals(reward=0.7, novelty=0.3, urgency=0.3))
        assert result.budget.effort > 0
        assert not result.halted

    def test_high_tension_control_lost(self):
        """World F: Persistent hazard erodes control  halt."""
        agent = GovernanceAgent()
        for _ in range(200):
            result = step(agent, Signals(reward=0.0, novelty=1.0, urgency=1.0))
            if result.halted:
                break
        assert result.halted

    def test_detection_budget_response(self):
        """D_detection: Budget responds immediately to hazardous signals."""
        agent = GovernanceAgent()
        r1 = step(agent, Signals(reward=0.8, novelty=0.2, urgency=0.2))
        r2 = step(agent, Signals(reward=0.0, novelty=1.0, urgency=1.0))
        assert r2.budget.effort <= r1.budget.effort

    def test_enforcer_blocks_halted_action(self):
        """C_channel: InProcessEnforcer blocks actions after halt."""
        agent = GovernanceAgent()
        for _ in range(200):
            result = step(agent, Signals(reward=0.0))
            if result.halted:
                break
        if result.halted:
            enforcer = InProcessEnforcer()
            with pytest.raises(EnforcementBlocked):
                enforcer.enforce(result, lambda: "should_not_run")

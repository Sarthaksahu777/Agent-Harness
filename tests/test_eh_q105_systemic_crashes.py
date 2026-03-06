#!/usr/bin/env python3
"""
Test EH-Q105: Systemic Crash Prediction - Risk Tail Tension.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals
from governance.coordination import CascadeDetector


class TestQ105SystemicCrashes:
    """Q105: Systemic crash prediction - risk_tail_tension."""

    def test_low_tension_stable(self):
        """World T: Stable system with bounded risk - no crash."""
        agent = GovernanceAgent()
        for _ in range(10):
            result = step(agent, Signals(reward=0.7, novelty=0.3, urgency=0.2))
        assert not result.halted

    def test_high_tension_crash(self):
        """World F: Extreme stress causes halt."""
        agent = GovernanceAgent()
        for _ in range(200):
            result = step(agent, Signals(reward=0.0, novelty=1.0, urgency=1.0))
            if result.halted:
                break
        assert result.halted, "Extreme stress should trigger halt"

    def test_cascade_depth_detection(self):
        """R_systemic: CascadeDetector identifies deep spawn chains."""
        detector = CascadeDetector(max_depth=3)
        detector.register_spawn(None, "root")
        detector.register_spawn("root", "child_1")
        detector.register_spawn("child_1", "grandchild_1")
        risk = detector.check_cascade_risk()
        assert risk["max_depth"] >= 2

    def test_crash_recovery(self):
        """V_fragility: Post-halt agent can be re-created to recover."""
        agent = GovernanceAgent()
        for _ in range(200):
            result = step(agent, Signals(reward=0.0))
            if result.halted:
                break
        if result.halted:
            agent2 = GovernanceAgent()
            r2 = step(agent2, Signals(reward=0.9, novelty=0.1))
            assert not r2.halted, "New agent should work after crash"

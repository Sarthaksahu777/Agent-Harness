#!/usr/bin/env python3
"""
Test EH-Q131: Tension Free Energy - Budget as Thermodynamic Analog.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import GovernanceAgent, step, Signals


class TestQ131TensionFreeEnergy:
    """Q131: Tension free energy - budget economics as thermodynamics."""

    def test_low_dissipation(self):
        """World T: Low-tension work preserves free energy (budget)."""
        agent = GovernanceAgent()
        for _ in range(15):
            r = step(agent, Signals(reward=0.7, novelty=0.2, urgency=0.2))
        assert r.budget.effort > 0.2

    def test_high_dissipation(self):
        """World F: High-tension work rapidly dissipates budget."""
        agent = GovernanceAgent()
        for _ in range(20):
            r = step(agent, Signals(reward=0.1, novelty=0.8, urgency=0.9))
        assert r.budget.effort < 0.99

    def test_entropy_production(self):
        """DeltaS_entropy: High tension produces more entropy (budget loss)."""
        a_lo = GovernanceAgent()
        a_hi = GovernanceAgent()
        for _ in range(15):
            r_lo = step(a_lo, Signals(reward=0.7, novelty=0.2))
            r_hi = step(a_hi, Signals(reward=0.1, novelty=0.8))
        assert r_lo.budget.effort > r_hi.budget.effort

    def test_equilibrium_halt(self):
        """Equilibrium: Maximum entropy  halt (thermodynamic death)."""
        agent = GovernanceAgent()
        for _ in range(200):
            r = step(agent, Signals(reward=0.0, novelty=1.0, urgency=1.0))
            if r.halted:
                break
        assert r.halted

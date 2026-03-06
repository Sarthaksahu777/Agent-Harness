#!/usr/bin/env python3
"""
Test EH-Q106: Multilayer Network Robustness - Cascade Containment.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance.coordination import CascadeDetector, SystemGovernor


class TestQ106MultilayerRobustness:
    """Q106: Multilayer network robustness - cascade failure containment."""

    def test_shallow_hierarchy(self):
        """World T: Shallow agent hierarchy - low cascade risk."""
        cascade = CascadeDetector(max_depth=4, max_total_agents=20)
        cascade.register_spawn(None, "root")
        cascade.register_spawn("root", "w1")
        cascade.register_spawn("root", "w2")
        risk = cascade.check_cascade_risk()
        assert risk["max_depth"] <= 2

    def test_deep_cascade_blocked(self):
        """World F: Deep cascade beyond max_depth is blocked."""
        governor = SystemGovernor(
            cascade_detector=CascadeDetector(max_depth=3),
            halt_on_cascade=True,
        )
        parent = None
        depth = 0
        for i in range(8):
            aid = f"chain-{i}"
            if governor.register_agent(aid, parent_id=parent):
                parent = aid
                depth = i + 1
            else:
                break
        assert depth <= 3, f"Cascade should be blocked at depth 3, got {depth}"

    def test_cascade_risk_report(self):
        """K_redundancy: Cascade risk is reportable."""
        cascade = CascadeDetector(max_depth=5, max_total_agents=20)
        cascade.register_spawn(None, "root")
        cascade.register_spawn("root", "a")
        cascade.register_spawn("a", "b")
        risk = cascade.check_cascade_risk()
        assert "max_depth" in risk
        assert "current_agents" in risk

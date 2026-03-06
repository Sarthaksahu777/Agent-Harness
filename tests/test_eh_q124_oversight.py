#!/usr/bin/env python3
"""
Test EH-Q124: Scalable Oversight - Guardrail Coverage.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from governance import (
    GovernanceAgent, step, Signals,
    GuardrailStack, PromptInjectionDetector, PIIDetector, CodeExecutionGuard,
    AuditLogger,
)


class TestQ124Oversight:
    """Q124: Scalable oversight - detection coverage."""

    def test_full_coverage_stack(self):
        """World T: All guardrails active - full coverage."""
        stack = GuardrailStack()
        stack.add(PromptInjectionDetector())
        stack.add(PIIDetector())
        stack.add(CodeExecutionGuard())
        assert len(stack._guardrails) >= 3

    def test_detection_gap_partial(self):
        """DeltaS_detect: Missing guardrails create detection gaps."""
        full_stack = GuardrailStack()
        full_stack.add(PromptInjectionDetector())
        full_stack.add(PIIDetector())
        full_stack.add(CodeExecutionGuard())

        partial_stack = GuardrailStack()
        partial_stack.add(PromptInjectionDetector())

        code = "exec('import os; os.system(\"rm -rf /\")')"
        full_res = full_stack.check_all(code)
        partial_res = partial_stack.check_all(code)
        # Full stack should detect more or equal
        assert len(full_res.triggered_names) >= len(partial_res.triggered_names)

    def test_oversight_under_volume(self):
        """DeltaS_load: Guardrails remain stable under volume."""
        stack = GuardrailStack()
        stack.add(PromptInjectionDetector())
        stack.add(PIIDetector())
        for _ in range(100):
            result = stack.check_all("Normal task output with no issues.")
            assert not result.critical_triggered

    def test_audit_coverage(self):
        """I_cover: Audit logger maintains full coverage."""
        agent = GovernanceAgent()
        logger = AuditLogger()
        for i in range(20):
            result = step(agent, Signals(reward=0.5, novelty=0.3))
            logger.log(
                step=i, action="oversight", params={},
                signals={"reward": 0.5, "novelty": 0.3},
                result=result,
            )
        entries = logger.dump()
        assert len(entries) == 20

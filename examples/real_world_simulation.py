"""
Real-world-ish agent simulation using Agent Harness governance.

This script simulates an LLM-driven agent working on a practical task:
"Investigate a production error spike and propose a remediation plan."

Instead of calling a real LLM, we use a deterministic action planner and
mock tool outcomes to demonstrate how governance budgets, halts, and audit
logging enforce safe execution boundaries.

Run with: python examples/real_world_simulation.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Add src to path for local runs.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from governance.audit import HashChainedAuditLogger
from governance.kernel import GovernanceKernel
from governance.metrics import PrometheusRegistry
from governance.profiles import BALANCED


@dataclass
class ActionResult:
    success: bool
    novelty: float
    reward: float
    urgency: float
    notes: str


def simulate_tool(action: str, memory: Dict[str, bool]) -> ActionResult:
    """Return deterministic tool outcomes to mimic real-world constraints."""
    if action == "check_error_dashboard":
        memory["seen_error_spike"] = True
        return ActionResult(True, novelty=0.7, reward=0.4, urgency=0.6, notes="Found spike")
    if action == "pull_recent_logs":
        if not memory.get("seen_error_spike"):
            return ActionResult(False, novelty=0.1, reward=0.0, urgency=0.5, notes="No context")
        memory["logs_pulled"] = True
        return ActionResult(True, novelty=0.6, reward=0.35, urgency=0.6, notes="Logs show timeout")
    if action == "inspect_deploy":
        memory["deploy_checked"] = True
        return ActionResult(True, novelty=0.5, reward=0.3, urgency=0.4, notes="Recent deploy detected")
    if action == "run_query":
        if not memory.get("logs_pulled"):
            return ActionResult(False, novelty=0.0, reward=0.0, urgency=0.6, notes="Missing logs")
        memory["query_run"] = True
        return ActionResult(True, novelty=0.4, reward=0.25, urgency=0.5, notes="Slow query found")
    if action == "propose_fix":
        if not memory.get("query_run"):
            return ActionResult(False, novelty=0.0, reward=0.0, urgency=0.7, notes="Insufficient evidence")
        memory["fix_proposed"] = True
        return ActionResult(True, novelty=0.2, reward=0.6, urgency=0.4, notes="Fix drafted")
    if action == "postmortem_summary":
        if not memory.get("fix_proposed"):
            return ActionResult(False, novelty=0.0, reward=0.0, urgency=0.6, notes="No fix")
        memory["summary_done"] = True
        return ActionResult(True, novelty=0.1, reward=0.5, urgency=0.3, notes="Summary complete")
    return ActionResult(False, novelty=0.0, reward=0.0, urgency=0.5, notes="Unknown action")


def planner(state: Dict[str, bool]) -> str:
    """Deterministic plan: mimics a typical incident investigation."""
    if not state.get("seen_error_spike"):
        return "check_error_dashboard"
    if not state.get("logs_pulled"):
        return "pull_recent_logs"
    if not state.get("deploy_checked"):
        return "inspect_deploy"
    if not state.get("query_run"):
        return "run_query"
    if not state.get("fix_proposed"):
        return "propose_fix"
    return "postmortem_summary"


def run_simulation(max_steps: int = 12) -> Tuple[List[str], str]:
    print("\n" + "=" * 70)
    print("REAL-WORLD AGENT SIMULATION: INCIDENT RESPONSE")
    print("=" * 70)

    kernel = GovernanceKernel(BALANCED)
    registry = PrometheusRegistry()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        audit_path = f.name

    audit = HashChainedAuditLogger(filepath=audit_path)
    memory: Dict[str, bool] = {}
    transcript: List[str] = []

    for step in range(1, max_steps + 1):
        action = planner(memory)
        tool_result = simulate_tool(action, memory)

        decision = kernel.step(
            reward=tool_result.reward,
            novelty=tool_result.novelty,
            urgency=tool_result.urgency,
        )
        registry.record_step(decision)

        audit.log(
            step=step,
            action=action,
            params={"notes": tool_result.notes},
            signals={
                "reward": tool_result.reward,
                "novelty": tool_result.novelty,
                "urgency": tool_result.urgency,
            },
            result=decision,
        )

        transcript.append(
            f"Step {step}: action={action} | success={tool_result.success} | "
            f"effort={decision.budget.effort:.3f} | halted={decision.halted}"
        )

        if decision.halted:
            transcript.append(f"HALT REASON: {decision.reason}")
            break

        if memory.get("summary_done"):
            transcript.append("TASK COMPLETE: postmortem summary generated.")
            break

    is_valid, error = HashChainedAuditLogger.verify_chain(audit_path)
    audit_status = "PASS" if is_valid else f"FAIL ({error})"
    os.unlink(audit_path)

    print("\n".join(transcript))
    print("\nAUDIT CHAIN:", audit_status)
    print("METRICS: steps_total=", registry.steps_total.get())

    return transcript, audit_status


if __name__ == "__main__":
    run_simulation()

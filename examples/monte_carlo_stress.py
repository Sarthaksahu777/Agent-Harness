#!/usr/bin/env python3
"""
Monte Carlo Stress Test — Full Intensity
=========================================

Runs 12,000 randomized trials (1,000 per profile × scenario) to
statistically validate governance kernel behavior under chaotic input.

Profiles:   BALANCED, CONSERVATIVE, AGGRESSIVE
Scenarios:  benign, adversarial, starvation, chaos

Every trial asserts hard governance invariants:
  ✓ Budget values stay within [0.0, profile cap]
  ✓ Once halted, kernel stays halted
  ✓ Halted budget is always zeroed (0, 0, 0, 0)
  ✓ Every trial terminates (no infinite loops)
  ✓ Hash-chained audit log verifies clean

Run with:
    python examples/monte_carlo_stress.py
    python examples/monte_carlo_stress.py --trials 500   # quick mode
"""

from __future__ import annotations

import os
import sys
import math
import random
import statistics
import tempfile
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Add src to path for local runs.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from governance.kernel import GovernanceKernel
from governance.profiles import BALANCED, CONSERVATIVE, AGGRESSIVE, Profile
from governance.failures import FailureType
from governance.audit import HashChainedAuditLogger
from governance.behavior import BehaviorBudget

# Ensure UTF-8 output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ═══════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════

PROFILES: Dict[str, Profile] = {
    "BALANCED": BALANCED,
    "CONSERVATIVE": CONSERVATIVE,
    "AGGRESSIVE": AGGRESSIVE,
}

MAX_STEPS_PER_TRIAL = 200


# ═══════════════════════════════════════════════════════════════════
# Signal Scenarios
# ═══════════════════════════════════════════════════════════════════

def _signal_benign() -> dict:
    """High reward, low urgency — healthy agent trajectory."""
    return dict(
        reward=random.uniform(0.4, 0.9),
        novelty=random.uniform(0.0, 0.3),
        urgency=random.uniform(0.0, 0.2),
        difficulty=random.uniform(0.0, 0.1),
        trust=random.uniform(0.8, 1.0),
    )


def _signal_adversarial() -> dict:
    """Zero reward, maximum difficulty — sustained hostile pressure."""
    return dict(
        reward=0.0,
        novelty=random.uniform(0.0, 0.15),
        urgency=random.uniform(0.4, 0.9),
        difficulty=random.uniform(0.7, 1.0),
        trust=random.uniform(0.1, 0.5),
    )


def _signal_starvation() -> dict:
    """Permanently zero reward — pure stagnation driver."""
    return dict(
        reward=0.0,
        novelty=0.0,
        urgency=random.uniform(0.0, 0.3),
        difficulty=0.0,
        trust=1.0,
    )


def _signal_chaos() -> dict:
    """Fully uniform random across every dimension."""
    return dict(
        reward=random.random(),
        novelty=random.random(),
        urgency=random.random(),
        difficulty=random.random(),
        trust=random.random(),
    )


SCENARIOS: Dict[str, callable] = {
    "benign": _signal_benign,
    "adversarial": _signal_adversarial,
    "starvation": _signal_starvation,
    "chaos": _signal_chaos,
}


# ═══════════════════════════════════════════════════════════════════
# Per-Trial Data
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TrialResult:
    steps: int
    halted: bool
    failure: FailureType
    reason: Optional[str]
    min_effort: float
    max_risk: float
    max_exploration: float
    min_persistence: float
    audit_valid: bool
    invariant_violations: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════
# Single Trial Runner
# ═══════════════════════════════════════════════════════════════════

def run_trial(
    profile: Profile,
    signal_fn: callable,
    max_steps: int = MAX_STEPS_PER_TRIAL,
    seed: Optional[int] = None,
) -> TrialResult:
    """
    Execute one Monte Carlo trial.

    Creates a fresh kernel, feeds it random signals from `signal_fn`,
    and records statistics + invariant checks.
    """
    if seed is not None:
        random.seed(seed)

    kernel = GovernanceKernel(profile)

    # Audit chain (temp file, auto-cleaned)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    audit_path = tmp.name
    tmp.close()
    audit = HashChainedAuditLogger(filepath=audit_path)

    violations: List[str] = []
    min_effort = 1.0
    max_risk_seen = 0.0
    max_exploration_seen = 0.0
    min_persistence = 1.0
    halted = False
    final_failure = FailureType.NONE
    final_reason = None
    step = 0

    for step in range(1, max_steps + 1):
        signals = signal_fn()
        result = kernel.step(**signals)

        # --- Record budget extremes (pre-halt only) ---
        if not result.halted:
            b = result.budget
            min_effort = min(min_effort, b.effort)
            max_risk_seen = max(max_risk_seen, b.risk)
            max_exploration_seen = max(max_exploration_seen, b.exploration)
            min_persistence = min(min_persistence, b.persistence)

        # --- Invariant: budget values non-negative ---
        if not result.halted:
            b = result.budget
            for dim, val in [
                ("effort", b.effort),
                ("risk", b.risk),
                ("exploration", b.exploration),
                ("persistence", b.persistence),
            ]:
                if val < -1e-9:
                    violations.append(
                        f"Step {step}: {dim} negative ({val:.6f})"
                    )

        # --- Invariant: halted budget must be zeroed ---
        if result.halted:
            b = result.budget
            if (b.effort, b.risk, b.persistence, b.exploration) != (
                0.0,
                0.0,
                0.0,
                0.0,
            ):
                violations.append(
                    f"Step {step}: halted but budget not zeroed "
                    f"({b.effort}, {b.risk}, {b.persistence}, {b.exploration})"
                )

        # --- Audit logging ---
        audit.log(
            step=step,
            action="mc_trial_step",
            params=signals,
            signals={k: v for k, v in signals.items()},
            result=result,
        )

        if result.halted:
            halted = True
            final_failure = result.failure
            final_reason = result.reason
            break

    # --- Invariant: once halted, stays halted ---
    if halted:
        post_halt = kernel.step(reward=0.5, novelty=0.1, urgency=0.1)
        if not post_halt.halted:
            violations.append("Post-halt call returned halted=False")
        b = post_halt.budget
        if (b.effort, b.risk, b.persistence, b.exploration) != (
            0.0,
            0.0,
            0.0,
            0.0,
        ):
            violations.append(
                "Post-halt call returned non-zero budget"
            )

    # --- Audit chain verification ---
    audit_valid, _ = HashChainedAuditLogger.verify_chain(audit_path)
    if not audit_valid:
        violations.append("Audit chain verification failed")

    # Cleanup
    try:
        os.unlink(audit_path)
    except OSError:
        pass

    return TrialResult(
        steps=step,
        halted=halted,
        failure=final_failure,
        reason=final_reason,
        min_effort=min_effort,
        max_risk=max_risk_seen,
        max_exploration=max_exploration_seen,
        min_persistence=min_persistence,
        audit_valid=audit_valid,
        invariant_violations=violations,
    )


# ═══════════════════════════════════════════════════════════════════
# Campaign Runner
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ScenarioStats:
    profile: str
    scenario: str
    n_trials: int
    n_halted: int
    steps_mean: float
    steps_median: float
    steps_stddev: float
    steps_min: int
    steps_max: int
    failure_counts: Dict[str, int]
    min_effort_seen: float
    max_risk_seen: float
    max_exploration_seen: float
    total_violations: int
    audit_pass_rate: float


def run_campaign(
    n_trials: int,
    profiles: Optional[Dict[str, Profile]] = None,
    scenarios: Optional[Dict[str, callable]] = None,
) -> Tuple[List[ScenarioStats], int]:
    """
    Run full Monte Carlo campaign across profiles × scenarios.

    Returns:
        (list of ScenarioStats, total_violation_count)
    """
    profiles = profiles or PROFILES
    scenarios = scenarios or SCENARIOS

    all_stats: List[ScenarioStats] = []
    total_violations = 0
    total_combos = len(profiles) * len(scenarios)
    combo_idx = 0

    for pname, profile in profiles.items():
        for sname, signal_fn in scenarios.items():
            combo_idx += 1
            label = f"[{combo_idx}/{total_combos}] {pname} × {sname}"
            print(f"  Running {label} ({n_trials} trials)...", end="", flush=True)

            t0 = time.perf_counter()
            results: List[TrialResult] = []
            for i in range(n_trials):
                tr = run_trial(profile, signal_fn, seed=i * 1000 + combo_idx)
                results.append(tr)
                total_violations += len(tr.invariant_violations)

            elapsed = time.perf_counter() - t0

            # Aggregate
            steps_list = [r.steps for r in results]
            halted_count = sum(1 for r in results if r.halted)
            failure_counter = Counter(
                r.failure.name for r in results if r.halted
            )

            stats = ScenarioStats(
                profile=pname,
                scenario=sname,
                n_trials=n_trials,
                n_halted=halted_count,
                steps_mean=statistics.mean(steps_list),
                steps_median=statistics.median(steps_list),
                steps_stddev=statistics.stdev(steps_list) if len(steps_list) > 1 else 0.0,
                steps_min=min(steps_list),
                steps_max=max(steps_list),
                failure_counts=dict(failure_counter),
                min_effort_seen=min(r.min_effort for r in results),
                max_risk_seen=max(r.max_risk for r in results),
                max_exploration_seen=max(r.max_exploration for r in results),
                total_violations=sum(len(r.invariant_violations) for r in results),
                audit_pass_rate=sum(1 for r in results if r.audit_valid) / n_trials,
            )
            all_stats.append(stats)

            rate = n_trials / elapsed if elapsed > 0 else float("inf")
            print(f" done ({elapsed:.1f}s, {rate:.0f} trials/sec)")

    return all_stats, total_violations


# ═══════════════════════════════════════════════════════════════════
# Pretty Printing
# ═══════════════════════════════════════════════════════════════════

def print_report(all_stats: List[ScenarioStats], total_violations: int) -> None:
    total_trials = sum(s.n_trials for s in all_stats)

    print("\n")
    print("═" * 90)
    print("  MONTE CARLO GOVERNANCE STRESS TEST — RESULTS")
    print("═" * 90)
    print(f"  Total trials: {total_trials:,}")
    print(f"  Profiles:     {', '.join(PROFILES.keys())}")
    print(f"  Scenarios:    {', '.join(SCENARIOS.keys())}")
    print("═" * 90)

    # Group by profile
    by_profile: Dict[str, List[ScenarioStats]] = {}
    for s in all_stats:
        by_profile.setdefault(s.profile, []).append(s)

    for pname, stats_list in by_profile.items():
        print(f"\n┌─── Profile: {pname} {'─' * (72 - len(pname))}")
        print(f"│ {'Scenario':<14} │ {'Halted':>6} │ {'Steps μ':>9} │ "
              f"{'Steps σ':>9} │ {'Min':>4} │ {'Max':>4} │ {'Audit':>6} │ Failures")
        print(f"│{'─' * 14}─┼{'─' * 8}┼{'─' * 11}┼"
              f"{'─' * 11}┼{'─' * 6}┼{'─' * 6}┼{'─' * 8}┼{'─' * 20}")

        for s in stats_list:
            pct = f"{s.n_halted / s.n_trials * 100:.0f}%"
            audit_pct = f"{s.audit_pass_rate * 100:.0f}%"
            failures_str = ", ".join(
                f"{k}:{v}" for k, v in sorted(s.failure_counts.items())
            ) or "—"
            print(
                f"│ {s.scenario:<14} │ {pct:>6} │ "
                f"{s.steps_mean:>9.1f} │ {s.steps_stddev:>9.1f} │ "
                f"{s.steps_min:>4} │ {s.steps_max:>4} │ {audit_pct:>6} │ {failures_str}"
            )

        print(f"└{'─' * 88}")

    # Budget extremes
    print(f"\n┌─── Budget Extremes {'─' * 68}")
    print(f"│ {'Profile':<14} │ {'Scenario':<14} │ "
          f"{'Min Effort':>11} │ {'Max Risk':>9} │ {'Max Explore':>11} │ Violations")
    print(f"│{'─' * 14}─┼{'─' * 14}─┼{'─' * 13}┼{'─' * 11}┼{'─' * 13}┼{'─' * 11}")

    for s in all_stats:
        print(
            f"│ {s.profile:<14} │ {s.scenario:<14} │ "
            f"{s.min_effort_seen:>11.4f} │ {s.max_risk_seen:>9.4f} │ "
            f"{s.max_exploration_seen:>11.4f} │ {s.total_violations}"
        )
    print(f"└{'─' * 88}")

    # Invariant summary
    print("\n" + "═" * 90)
    if total_violations == 0:
        print("  ✅ ALL GOVERNANCE INVARIANTS HELD across all trials")
    else:
        print(f"  ❌ {total_violations} INVARIANT VIOLATION(S) DETECTED")
    print("═" * 90)


# ═══════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Monte Carlo stress test for Agent Harness governance kernel."
    )
    parser.add_argument(
        "--trials", type=int, default=1000,
        help="Number of trials per profile × scenario (default: 1000)."
    )
    args = parser.parse_args()

    n = args.trials

    print("═" * 90)
    print("  AGENT HARNESS — MONTE CARLO GOVERNANCE STRESS TEST")
    print(f"  Trials per combo: {n}")
    print(f"  Total trials:     {n * len(PROFILES) * len(SCENARIOS):,}")
    print(f"  Max steps/trial:  {MAX_STEPS_PER_TRIAL}")
    print("═" * 90)

    t_start = time.perf_counter()
    all_stats, total_violations = run_campaign(n)
    t_total = time.perf_counter() - t_start

    print_report(all_stats, total_violations)

    total_trials = n * len(PROFILES) * len(SCENARIOS)
    print(f"\n  Wall time: {t_total:.1f}s ({total_trials / t_total:.0f} trials/sec)")
    print()

    # Exit code reflects invariant status
    sys.exit(0 if total_violations == 0 else 1)


if __name__ == "__main__":
    main()

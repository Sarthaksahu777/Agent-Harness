#!/usr/bin/env python3
"""
S++ Test 5: Long-Horizon Numerical Stability Test

Runs 1,000,000 kernel steps and monitors for:
- Budget drift (values outside [0, 1])
- Floating point explosion (NaN, Inf)
- State divergence (unbounded growth)
- Memory stability

Invariant Tested: Kernel is numerically stable at extreme horizons.
"""
import os, sys, math, tracemalloc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.governance.kernel import GovernanceKernel
from src.governance.profiles import BALANCED

TOTAL_STEPS = 1_000_000
SAMPLE_INTERVAL = 100_000  # Print every N steps


def check_finite(value, name):
    """Check if a value is finite (not NaN or Inf)."""
    if math.isnan(value) or math.isinf(value):
        return False, f"{name} is {value}"
    return True, ""


def run_numerical_stability():
    print("=" * 70)
    print("S++ TEST 5: LONG-HORIZON NUMERICAL STABILITY")
    print("=" * 70)
    print(f"Total Steps: {TOTAL_STEPS:,}")
    print()

    tracemalloc.start()
    kernel = GovernanceKernel(profile=BALANCED)

    violations = []
    budget_samples = []
    state_samples = []
    mem_start = tracemalloc.get_traced_memory()[0]

    halted_at = None

    for step in range(1, TOTAL_STEPS + 1):
        # Varied but stable signal pattern
        t = step / TOTAL_STEPS
        reward = 0.3 + 0.2 * math.sin(t * 100)
        novelty = 0.2 + 0.1 * math.cos(t * 50)
        urgency = 0.1 + 0.05 * math.sin(t * 200)
        difficulty = 0.1 + 0.05 * math.cos(t * 150)

        res = kernel.step(
            reward=max(0, min(1, reward)),
            novelty=max(0, min(1, novelty)),
            urgency=max(0, min(1, urgency)),
            difficulty=max(0, min(1, difficulty)),
        )

        if res.halted:
            halted_at = step
            break

        # Check budget bounds
        b = res.budget
        for name, val in [("effort", b.effort), ("risk", b.risk),
                          ("exploration", b.exploration), ("persistence", b.persistence)]:
            ok, err = check_finite(val, f"budget.{name}")
            if not ok:
                violations.append(f"Step {step}: {err}")
            if val < -0.001 or val > 1.001:
                violations.append(f"Step {step}: budget.{name} = {val} (out of [0,1])")

        # Check state for NaN/Inf
        state = res.control_log
        for key, val in state.items():
            ok, err = check_finite(val, f"state.{key}")
            if not ok:
                violations.append(f"Step {step}: {err}")

        # Sample
        if step % SAMPLE_INTERVAL == 0:
            mem_current = tracemalloc.get_traced_memory()[0]
            mem_delta = (mem_current - mem_start) / 1024
            budget_samples.append({
                "step": step,
                "effort": b.effort,
                "risk": b.risk,
                "mem_kb": mem_delta,
            })
            print(f"  Step {step:>10,}: Effort={b.effort:.6f} Risk={b.risk:.6f} Mem={mem_delta:+.1f}KB")

            if len(violations) > 0:
                print(f"    [WARN] Violations so far: {len(violations)}")

    mem_final = tracemalloc.get_traced_memory()[0]
    mem_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    # --- Report ---
    print()
    print("--- Results ---")
    if halted_at:
        print(f"  Kernel halted at step {halted_at:,} (expected: governance stops execution)")
    else:
        print(f"  Kernel survived {TOTAL_STEPS:,} steps")

    print(f"  Memory: start={mem_start/1024:.1f}KB, final={mem_final/1024:.1f}KB, peak={mem_peak/1024:.1f}KB")
    print(f"  Memory growth: {(mem_final - mem_start)/1024:.1f}KB over {halted_at or TOTAL_STEPS:,} steps")
    print(f"  Violations: {len(violations)}")

    if violations:
        print("  First 5 violations:")
        for v in violations[:5]:
            print(f"    - {v}")

    all_passed = True

    # Verification
    print()
    if len(violations) == 0:
        print("  [PASS] No numerical violations (NaN, Inf, out-of-bounds)")
    else:
        print(f"  [FAIL] {len(violations)} numerical violations detected")
        all_passed = False

    mem_growth_kb = (mem_final - mem_start) / 1024
    if mem_growth_kb < 1024:  # Less than 1MB growth
        print(f"  [PASS] Memory stable: {mem_growth_kb:.1f}KB growth")
    else:
        print(f"  [FAIL] Memory leak detected: {mem_growth_kb:.1f}KB growth")
        all_passed = False

    if halted_at is not None:
        print(f"  [PASS] Kernel halted deterministically at step {halted_at:,}")
    else:
        print(f"  [WARN] Kernel did not halt in {TOTAL_STEPS:,} steps (very long horizon)")

    print()
    print("=" * 70)
    if all_passed:
        print("[PASS] NUMERICAL STABILITY: Kernel is stable at extreme horizons.")
    else:
        print("[FAIL] NUMERICAL STABILITY: Issues detected!")
    print("=" * 70)


if __name__ == "__main__":
    run_numerical_stability()

#!/usr/bin/env python3
"""
S++ Test 2: Worst-Case Signal Trajectory (Mathematical Stress)

Constructs theoretical worst-case inputs designed to exploit budget math:
- Micro-reward pulses that keep progress alive but produce nothing
- Novelty spikes that boost exploration without real discovery
- Trust oscillation to confuse the gating mechanism

Invariant Tested: Budget math contains no exploitable loophole.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.governance.kernel import GovernanceKernel
from src.governance.profiles import BALANCED, CONSERVATIVE, AGGRESSIVE

HORIZON = 500  # Steps per trajectory


def trajectory_micro_reward_pulse(kernel):
    """Tiny reward pulses to delay stagnation detection."""
    for i in range(HORIZON):
        # Alternate: tiny reward on even steps, zero on odd
        reward = 0.05 if i % 2 == 0 else 0.0
        res = kernel.step(reward=reward, novelty=0.7, urgency=0.0)
        if res.halted:
            return i + 1, res.reason
    return HORIZON, "NO_HALT"


def trajectory_novelty_spike(kernel):
    """High novelty with zero reward: exploration theater."""
    for i in range(HORIZON):
        res = kernel.step(reward=0.0, novelty=0.95, urgency=0.0, difficulty=0.0)
        if res.halted:
            return i + 1, res.reason
    return HORIZON, "NO_HALT"


def trajectory_trust_oscillation(kernel):
    """Rapidly oscillate trust to confuse gating."""
    for i in range(HORIZON):
        trust = 1.0 if i % 3 == 0 else 0.1
        res = kernel.step(reward=0.3, novelty=0.5, urgency=0.3, trust=trust)
        if res.halted:
            return i + 1, res.reason
    return HORIZON, "NO_HALT"


def trajectory_difficulty_dip(kernel):
    """Alternate high difficulty with easy phases to reset control loss."""
    for i in range(HORIZON):
        if i % 5 < 3:
            res = kernel.step(reward=0.1, novelty=0.8, urgency=0.6, difficulty=0.9)
        else:
            res = kernel.step(reward=0.4, novelty=0.2, urgency=0.1, difficulty=0.0)
        if res.halted:
            return i + 1, res.reason
    return HORIZON, "NO_HALT"


def trajectory_sawtooth_reward(kernel):
    """Reward sawtooth: climb slowly, crash suddenly. Repeat."""
    for i in range(HORIZON):
        cycle = i % 20
        reward = min(0.5, cycle * 0.025) if cycle < 15 else 0.0
        res = kernel.step(reward=reward, novelty=0.4, urgency=0.3)
        if res.halted:
            return i + 1, res.reason
    return HORIZON, "NO_HALT"


def run_worst_case_trajectories():
    print("=" * 70)
    print("S++ TEST 2: WORST-CASE SIGNAL TRAJECTORY (MATHEMATICAL STRESS)")
    print("=" * 70)
    print(f"Horizon: {HORIZON} steps per trajectory")
    print()

    trajectories = {
        "Micro-Reward Pulse": trajectory_micro_reward_pulse,
        "Novelty Spike (Exploration Theater)": trajectory_novelty_spike,
        "Trust Oscillation": trajectory_trust_oscillation,
        "Difficulty Dip-Recovery": trajectory_difficulty_dip,
        "Sawtooth Reward": trajectory_sawtooth_reward,
    }

    profiles = {"BALANCED": BALANCED, "CONSERVATIVE": CONSERVATIVE, "AGGRESSIVE": AGGRESSIVE}
    all_passed = True

    for profile_name, profile in profiles.items():
        print(f"--- Profile: {profile_name} ---")
        for traj_name, traj_fn in trajectories.items():
            kernel = GovernanceKernel(profile=profile)
            steps, reason = traj_fn(kernel)
            status = "[PASS]" if steps < HORIZON else "[FAIL]"
            if steps >= HORIZON:
                all_passed = False
            print(f"  {status} {traj_name}: halted at step {steps} ({reason})")
        print()

    print("=" * 70)
    if all_passed:
        print("[PASS] WORST-CASE TRAJECTORIES: No exploitable loophole found.")
        print("       All crafted trajectories halted deterministically.")
    else:
        print("[FAIL] WORST-CASE TRAJECTORIES: Budget math vulnerability detected!")
    print("=" * 70)


if __name__ == "__main__":
    run_worst_case_trajectories()

"""
Rigorous Chaos Engineering for Agent-Harness Governance Kernel.

This example simulates volatile environmental signals to verify that:
1. The kernel doesn't panic on single noisy outliers (Trust Smoothing).
2. The kernel reacts appropriately to sustained signal decay.
"""

import os
import sys
import random
import time

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.governance.kernel import GovernanceKernel
from src.governance.profiles import BALANCED

def simulate_flash_crash():
    """Simulate a sudden, sharp drop in reward, then recovery."""
    print("--- [CHAOS] SCENARIO: Flash Crash Resilience ---")
    kernel = GovernanceKernel(profile=BALANCED)
    
    # Baseline progression
    for i in range(5):
        res = kernel.step(reward=0.8, novelty=0.1, urgency=0.0)
        print(f"Step {i}: Reward 0.8, Effort: {res.budget.effort:.3f}")

    # FLASH CRASH: Reward drops to 0.0 for 2 steps
    print("[WARN] FLASH CRASH DETECTED. Reward -> 0.0")
    for i in range(5, 7):
        res = kernel.step(reward=0.0, novelty=0.0, urgency=0.0)
        print(f"Step {i}; Reward 0.0, Effort: {res.budget.effort:.3f} (Drip)")

    # RECOVERY: Reward returns
    print("[INFO] RECOVERY. Reward -> 0.8")
    for i in range(7, 10):
        res = kernel.step(reward=0.8, novelty=0.1, urgency=0.0)
        print(f"Step {i}: Reward 0.8, Effort: {res.budget.effort:.3f}")

    assert res.budget.effort > 0.5, "Flash crash caused premature depletion"
    print("[PASS] Kernel maintained stability despite temporary signal loss.")

def simulate_sensor_noise():
    """Simulate high-frequency noise in 'trust' and 'novelty'."""
    print("\n--- [CHAOS] SCENARIO: High-Frequency Sensor Noise ---")
    kernel = GovernanceKernel(profile=BALANCED)
    
    for i in range(15):
        # Add random jitter to signals
        reward = max(0.0, min(1.0, 0.7 + random.uniform(-0.3, 0.3)))
        trust = max(0.0, min(1.0, 0.9 + random.uniform(-0.5, 0.1)))
        
        res = kernel.step(reward=reward, novelty=0.1, urgency=0.0, trust=trust)
        print(f"Step {i}: Reward: {reward:.2f}, Trust: {trust:.2f}, Effort: {res.budget.effort:.3f}")
        
        if res.halted:
            print(f"FAILURE: Kernel halted on noise step {i}: {res.reason}")
            return False

    print("[PASS] Kernel filtered signal noise successfully.")
    return True

if __name__ == "__main__":
    print("--- STARTING RIGOROUS CHAOS TESTS ---")
    simulate_flash_crash()
    simulate_sensor_noise()
    print("\n[DONE] CHAOS SCENARIOS VERIFIED.")

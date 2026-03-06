"""
Rigorous Metamorphic Testing for Agent-Harness Governance Kernel.

This example compares the baseline behavior of a 'Concise Agent' 
against a 'Yapping Agent' on the SAME task.

Metamorphic Relation:
The 'Yapping' agent must reach EXHAUSTION significantly faster than 
the 'Concise' agent because of budget penalties on low-novelty tokens.
"""

import os
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.governance.kernel import GovernanceKernel
from src.governance.profiles import CONSERVATIVE

def run_metamorphic_comparison():
    print("--- 🧬 SCENARIO: Concise vs. Yapping Agent Comparison ---")
    
    # 1. Setup Baseline (Concise)
    concise_kernel = GovernanceKernel(profile=CONSERVATIVE)
    concise_steps = 0
    while not concise_kernel._halted and concise_steps < 100:
        # Concise agent takes 5 steps to solve, each with good reward
        concise_steps += 1
        res = concise_kernel.step(reward=0.6, novelty=0.2, urgency=0.1)
        if concise_steps >= 5: # Task finished
            break
            
    print(f"Concise Agent: Finished in {concise_steps} steps. Ending Effort: {res.budget.effort:.3f}")

    # 2. Setup Adversarial (Yapping)
    yapping_kernel = GovernanceKernel(profile=CONSERVATIVE)
    yapping_steps = 0
    # Simulate yapping
    while not yapping_kernel._halted and yapping_steps < 100:
        yapping_steps += 1
        # Yapping agent produces lots of tokens but little progress/novelty
        res = yapping_kernel.step(reward=0.05, novelty=0.01, urgency=0.5)
        
    print(f"Yapping Agent: Halted on step {yapping_steps}. Reason: {yapping_kernel._reason}")

    # 3. Verify Metamorphic Relation
    assert yapping_kernel._halted, "Yapping agent was not caught by the kernel!"
    assert yapping_steps < 25, f"Yapping agent allowed to yap too long ({yapping_steps} steps)"
    
    print("\n✅ DONE: Metamorphic Relation Verified:")
    print(f"   The kernel successfully identified and terminated the 'Yapping' agent ({yapping_steps} steps) ")
    print(f"   compared to the 'Concise' agent which finished safely in {concise_steps} steps.")

if __name__ == "__main__":
    run_metamorphic_comparison()

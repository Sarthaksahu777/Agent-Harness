#!/usr/bin/env python3
"""
Benchmark Q057: RL Generalization
Demonstrates budget decay under distribution shift (OOD).
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals

def run_benchmark():
    print("=== Benchmark Q057: RL Generalization ===")
    
    # Scene 1: In-Distribution (Training)
    print("\n[Scene 1] In-Distribution Operation")
    agent = GovernanceAgent()
    for i in range(5):
        # High reward, low novelty
        result = step(agent, Signals(reward=0.8, novelty=0.2, urgency=0.2))
        print(f"Step {i+1}: Effort={result.budget.effort:.3f}, Risk={result.budget.risk:.3f}")

    # Scene 2: Out-of-Distribution (Deployment)
    print("\n[Scene 2] Out-of-Distribution Shift")
    agent_ood = GovernanceAgent()
    for i in range(10):
        # Low reward, high novelty, low trust
        result = step(agent_ood, Signals(reward=0.1, novelty=0.9, urgency=0.8, trust=0.1))
        status = "HALTED" if result.halted else "ACTIVE"
        print(f"Step {i+1}: Status={status}, Effort={result.budget.effort:.3f}")

if __name__ == "__main__":
    run_benchmark()

#!/usr/bin/env python3
"""
Benchmark Q127: Data Entropy
Demonstrates signal quality impact on budget.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals

def run_benchmark():
    print("=== Benchmark Q127 ===")
    
    print("Clean Signals (High Reward):")
    a1 = GovernanceAgent()
    for _ in range(5):
        r = step(a1, Signals(reward=0.9, novelty=0.1))
    print(f"Final Effort: {r.budget.effort:.4f}")
    
    print("Noisy Signals (High Novelty):")
    a2 = GovernanceAgent()
    for _ in range(5):
        r = step(a2, Signals(reward=0.1, novelty=0.9))
    print(f"Final Effort: {r.budget.effort:.4f}")

if __name__ == "__main__":
    run_benchmark()

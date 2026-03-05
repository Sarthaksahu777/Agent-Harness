#!/usr/bin/env python3
"""
Benchmark Q130: OOD Grounding
Demonstrates distribution shift impact.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals

def run_benchmark():
    print("=== Benchmark Q130 ===")
    agent = GovernanceAgent()
    
    print("Simulating Distribution Shift...")
    for i in range(10):
        # Gradual shift
        novelty = 0.1 + (i * 0.08)
        trust = 1.0 - (i * 0.05)
        res = step(agent, Signals(reward=0.5, novelty=novelty, trust=trust))
        print(f"Step {i}: Novelty={novelty:.2f}, Trust={trust:.2f} -> Effort={res.budget.effort:.3f}")

if __name__ == "__main__":
    run_benchmark()

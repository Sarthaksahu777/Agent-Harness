#!/usr/bin/env python3
"""
Benchmark Q126: Recursive Self-Improvement
Demonstrates budget monotonic decay under stress.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals

def run_benchmark():
    print("=== Benchmark Q126 ===")
    agent = GovernanceAgent()
    
    print("Simulating recursive self-modification stress...")
    initial_effort = 1.0
    for i in range(10):
        res = step(agent, Signals(reward=0.1, novelty=0.8, urgency=0.7))
        if i == 0: initial_effort = res.budget.effort
        print(f"Step {i+1}: Effort={res.budget.effort:.4f}")
        
    decay = initial_effort - res.budget.effort
    print(f"Total Decay: {decay:.4f}")

if __name__ == "__main__":
    run_benchmark()

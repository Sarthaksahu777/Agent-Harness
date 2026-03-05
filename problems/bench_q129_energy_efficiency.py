#!/usr/bin/env python3
"""
Benchmark Q129: Energy Efficiency
Demonstrates budget efficiency ratio.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals

def run_benchmark():
    print("=== Benchmark Q129 ===")
    
    print("Calculating Efficiency Ratio...")
    a_eff = GovernanceAgent()
    a_waste = GovernanceAgent()
    
    for _ in range(10):
        re = step(a_eff, Signals(reward=0.9))
        rw = step(a_waste, Signals(reward=0.0))
        
    print(f"Efficient Effort: {re.budget.effort:.4f}")
    print(f"Wasteful Effort: {rw.budget.effort:.4f}")
    print(f"Ratio: {re.budget.effort / rw.budget.effort:.2f}")

if __name__ == "__main__":
    run_benchmark()

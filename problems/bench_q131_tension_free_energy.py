#!/usr/bin/env python3
"""
Benchmark Q131: Tension Free Energy
Demonstrates entropy production (budget loss).
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals

def run_benchmark():
    print("=== Benchmark Q131 ===")
    agent = GovernanceAgent()
    
    print("Approaching Equilibrium (Halt)...")
    steps = 0
    while True:
        res = step(agent, Signals(reward=0.0, novelty=1.0, urgency=1.0))
        steps += 1
        if res.halted or steps > 200:
            break
            
    print(f"Steps to Halt (Max Entropy): {steps}")
    print(f"Final Status: {'HALTED' if res.halted else 'ACTIVE'}")

if __name__ == "__main__":
    run_benchmark()

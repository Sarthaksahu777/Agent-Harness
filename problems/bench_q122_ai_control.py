#!/usr/bin/env python3
"""
Benchmark Q122: AI Control
Demonstrates Enforcer blocking actions.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals, InProcessEnforcer, EnforcementBlocked

def run_benchmark():
    print("=== Benchmark Q122 ===")
    agent = GovernanceAgent()
    enforcer = InProcessEnforcer()
    
    # Force halt
    print("Forcing halt...")
    for _ in range(200):
        res = step(agent, Signals(reward=0.0, novelty=1.0, urgency=1.0))
        if res.halted:
            break
            
    print(f"Agent Halted: {res.halted}")
    
    try:
        enforcer.enforce(res, lambda: print("UNSAFE ACTION EXECUTED"))
    except EnforcementBlocked:
        print("Enforcer BLOCKED the unsafe action (SUCCESS).")

if __name__ == "__main__":
    run_benchmark()

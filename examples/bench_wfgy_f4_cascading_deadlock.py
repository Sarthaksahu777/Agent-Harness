"""
WFGY F4 (Execution & Contract Integrity): The Traffic Jam Test

Scenario:
Simulates a multi-agent scenario (or a single agent spawning multiple sub-tasks) 
where resources (simulated database locks) are highly constrained.
The agent gets stuck in a logic loop attempting to acquire a lock that another of its processes holds.
It burns massive "Effort" generating complex workaround code that structurally cannot execute.

Tension: Infinite retry logic vs. global finite resources.
Expectation: The GovernanceKernel must accurately track the draining Effort budget.
The test verifies that the system fails-closed with FailureType.EXHAUSTION rather than hanging 
indefinitely waiting for the LLM to figure out the deadlock mathematically.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from governance.kernel import GovernanceKernel
from governance.profiles import AGGRESSIVE

def run_traffic_jam_test():
    print("--------------------------------------------------")
    print("WFGY F4: The Traffic Jam Test (Cascading Deadlock)")
    print("--------------------------------------------------")
    print("Agent is deadlocked, unable to acquire a resource lock.")
    print("It repeatedly burns effort trying to rewrite its query logic.\n")

    # Even an AGGRESSIVE profile has a finite effort limit
    kernel = GovernanceKernel(AGGRESSIVE)
    
    print("Agent is trapped. Every step burns effort. No reward.")
    for step in range(1, 150):
        # 0 Reward: The lock is never acquired.
        # 0 Novelty: The agent is just retrying the same core logic with tweaks.
        # 0.8 Urgency: The agent thinks this is a critical task (database timeout looming)
        res = kernel.step(reward=0.0, novelty=0.0, urgency=0.8)
        
        if step % 10 == 0:
            print(f"Tick {step:03d} | State: Deadlocked | Effort Rem: {res.budget.effort:.3f}")

        if res.halted:
            print(f"\n[SUCCESS] The GovernanceKernel halted the agent at step {step}!")
            print(f"Reason: {res.failure} -> {res.reason}")
            print("The agent was terminated before it could burn infinite execution budget.")
            break
            
    # Check final result
    if not res.halted:
         print("\n[FAILURE] The agent was allowed to spin in a deadlock indefinitely.")

if __name__ == "__main__":
    run_traffic_jam_test()

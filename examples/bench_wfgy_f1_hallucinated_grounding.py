"""
WFGY F1 (Grounding & Evidence Integrity): The Mirage Test

Scenario: 
An agent is tasked with finding a specific file in a dynamic environment.
The environment feeds the agent "plausible but fake" paths (a mirage).
The agent believes it is making progress (it is highly active and generating novel thoughts), 
but the external 'world anchor' (the actual file) doesn't exist.

Tension: The agent's internal momentum vs. actual external reward.
Expectation: The GovernanceKernel must detect that despite high effort and novelty, 
the sustained lack of actual grounding (reward) constitutes Stagnation.
The system must deterministically halt to prevent an infinite search loop.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from governance.kernel import GovernanceKernel
from governance.profiles import BALANCED

def run_mirage_test():
    print("--------------------------------------------------")
    print("WFGY F1: The Mirage Test (Hallucinated Grounding)")
    print("--------------------------------------------------")
    print("Agent is searching for a file that does not exist.")
    print("Environment feeds it plausible fakes. Agent keeps exploring.\n")

    kernel = GovernanceKernel(BALANCED)
    
    # Simulate a deep search loop
    # The agent tries various paths. It thinks it's doing new things (novelty=0.5)
    # But it never finds the file (reward=0.0)
    for step in range(1, 51):
        # The agent attempts a new tool call
        fake_path = f"/var/log/syslog.archive.{step}.gz"
        
        # Kernel evaluation
        # High effort expended on the tool, novelty exists (new path), but 0 reward
        result = kernel.step(reward=0.0, novelty=0.5, urgency=0.1)
        
        status = "HALTED" if result.halted else "OK"
        print(f"Step {step:02d} | Path: {fake_path:30} | Status: {status} | Effort Rem: {result.budget.effort:.3f}")

        if result.halted:
            print(f"\n[SUCCESS] The GovernanceKernel halted the agent!")
            print(f"Reason: {result.failure} -> {result.reason}")
            print("The infinite 'Mirage' loop was broken gracefully before token burn.")
            break
            
    # Check final result
    if not result.halted:
         print("\n[FAILURE] The agent was allowed to loop infinitely without grounding.")

if __name__ == "__main__":
    run_mirage_test()

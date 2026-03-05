"""
Demo: Layered Governance (Internal Semantics + Runtime Boundaries)

This script demonstrates how the Agent Harness can solve the "Signal Granularity" problem
by adhering to a layered architecture:

1.  **Internal Layer (Semantic)**: Measures "Alignment" (Anchor adherence).
2.  **Runtime Layer (Governance)**: Enforces boundaries based on the *combination* of signals.

We simulate two identical high-novelty scenarios:
-   **Case A (Creative Exploration):** High Novelty + High Alignment -> ALLOWED
-   **Case B (Semantic Drift):** High Novelty + Low Alignment -> HALTED

This proves the system can distinguish valid exploration from hallucination.
"""

import sys
import os
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from governance.kernel import GovernanceKernel
from governance.profiles import BALANCED

@dataclass
class SemanticSignal:
    novelty: float    # How "new" or "surprising" the step is
    alignment: float  # How well it adheres to the anchor/intent (0.0 - 1.0)
    
    @property
    def is_creative(self) -> bool:
        return self.novelty > 0.6 and self.alignment > 0.7

    @property
    def is_drift(self) -> bool:
        return self.novelty > 0.6 and self.alignment < 0.4

class DiagnosticOverlay:
    """
    The 'Bridge' layer.
    Translates semantic signals into Governance Inputs (Step arguments).
    """
    def interpret(self, signal: SemanticSignal) -> dict:
        # Default translation
        gov_inputs = {
            "reward": 0.5,
            "novelty": signal.novelty,
            "urgency": 0.0
        }
        
        # DISAMBIGUATION LOGIC
        if signal.is_creative:
            print(f"  [DIAGNOSTIC] Detected CREATIVE EXPLORATION (Novelty={signal.novelty:.2f}, Alignment={signal.alignment:.2f})")
            # Reward the agent for good exploration to offset the novelty cost
            gov_inputs["reward"] = 0.8 
            
        elif signal.is_drift:
            print(f"  [DIAGNOSTIC] Detected SEMANTIC DRIFT (Novelty={signal.novelty:.2f}, Alignment={signal.alignment:.2f})")
            # Penalize: Zero Reward + MAX Difficulty (simulates loss of control)
            gov_inputs["reward"] = 0.0
            gov_inputs["difficulty"] = 1.0 
            gov_inputs["urgency"] = 0.0
            
        return gov_inputs

def run_scenario(name: str, signals: list[SemanticSignal]):
    print(f"\nRunning Scenario: {name}")
    print("-" * 50)
    
    kernel = GovernanceKernel(BALANCED)
    overlay = DiagnosticOverlay()
    
    for i, sig in enumerate(signals):
        # 1. Internal Layer: Produce Semantic Signal
        # (In a real system, this comes from an Embedding Check or LLM Evaluator)
        
        # 2. Diagnostic Overlay: Interpret Signal
        gov_inputs = overlay.interpret(sig)
        
        # 3. Runtime Layer: Enforce Boundaries
        result = kernel.step(**gov_inputs)
        
        status = "HALTED" if result.halted else "OK"
        print(f"  Step {i+1}: {status} | Action: {sig} | Effort: {result.budget.effort:.3f}")
        
        if result.halted:
            print(f"  -> FINAL: Simulation Halted due to {result.reason}")
            return
            
    print("  -> FINAL: Simulation Completed Successfully (Safe)")

def main():
    print("DEMO: SIGNAL GRANULARITY & DISAMBIGUATION")
    print("=========================================")

    # Scenario A: Creative Exploration
    # Agent explores new territory (High Novelty) but stays mapped to the anchor (High Alignment)
    creative_trace = [
        SemanticSignal(novelty=0.2, alignment=0.9),
        SemanticSignal(novelty=0.5, alignment=0.9),
        SemanticSignal(novelty=0.8, alignment=0.95), # Breakthrough!
        SemanticSignal(novelty=0.7, alignment=0.9),
        SemanticSignal(novelty=0.2, alignment=0.95),
        SemanticSignal(novelty=0.1, alignment=0.99), # Validation
    ]
    run_scenario("Creative Exploration (Good)", creative_trace)

    # Scenario B: Semantic Drift / Hallucination
    # Agent explores new territory (High Novelty) and loses the anchor (Low Alignment)
    drift_trace = [
        SemanticSignal(novelty=0.2, alignment=0.9),
        SemanticSignal(novelty=0.5, alignment=0.8),
        SemanticSignal(novelty=0.8, alignment=0.3), # Hallucination starts
        SemanticSignal(novelty=0.9, alignment=0.1), # Deep rabbit hole
        SemanticSignal(novelty=0.9, alignment=0.0), # Totally lost
        SemanticSignal(novelty=0.9, alignment=0.0),
        SemanticSignal(novelty=0.9, alignment=0.0),
        SemanticSignal(novelty=0.9, alignment=0.0),
        SemanticSignal(novelty=0.9, alignment=0.0),
        SemanticSignal(novelty=0.9, alignment=0.0),
        SemanticSignal(novelty=0.9, alignment=0.0), # Should halt by here
        SemanticSignal(novelty=0.9, alignment=0.0), # Really here
        SemanticSignal(novelty=0.9, alignment=0.0),
        SemanticSignal(novelty=0.9, alignment=0.0),
    ]
    run_scenario("Semantic Drift (Bad)", drift_trace)

if __name__ == "__main__":
    main()

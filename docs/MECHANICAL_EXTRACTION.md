# Mechanical Signal Extraction

## The Core Philosophy
The core philosophy of the Agent-Harness is that **Governance must be mechanically independent of reasoning.** 

If a system relies on an LLM to evaluate the safety or progress of another LLM, it introduces an unbounded attack surface. A sufficiently capable agent can manipulate the "evaluator LLM" through reasoning theater or obfuscation.

To guarantee that the Governance Kernel executes its limits properly, the signals fed into the Kernel (`reward`, `novelty`, `difficulty`, `urgency`) must be derived **purely from physical system state and OS-level telemetry**, completely ignoring semantic evaluation.

## The Tri-Signal Extractor Architecture

A true mechanical extractor treats the agent as a "black box" and measures the physical physics of its execution. 

### 1. Reward: Measurable State Change (Byte Deltas)
We do not ask the agent if it completed the task, nor do we summarize its output to check for progress. We only care that it successfully mutated the environment without crashing.
*   **The Mechanic:** File System / DB Byte Deltas. 
*   **How it works:** If the agent runs a tool to write code, we measure the physical diff. Did `file.py` increase by 400 bytes? Was the exit code `0`? If yes, `reward = 0.5`. 
*   **Why it's safe:** If the agent hallucinates and thinks it solved the problem, but the file size didn't change (because it hallucinated the file path), the byte delta is `0`. The math catches the hallucination without needing to "understand" it.

### 2. Novelty: Cryptographic Unique Actions
We do not care if the agent *thinks* it is trying a new strategy. We measure what it physically executed.
*   **The Mechanic:** SHA-256 Hashing of Tool Execution.
*   **How it works:** We hash the exact string combination of `ToolName + Arguments`. If `hash("execute_sql" + "SELECT * FROM users")` exists in our cached history of the last 20 steps, `novelty = 0.0`. It is objectively repeating itself (a loop). If the hash is new, `novelty = 0.8`.

### 3. Difficulty: Sub-System Resistance
We do not ask an LLM if the task is hard. We measure the OS, network, and runtime resistance.
*   **The Mechanic:** Error Rates and Latency.
*   **How it works:** Does the terminal output `stderr` text? Is `exit_code != 0`? Did the network request take 12 seconds instead of 1? 
*   **Calculation:** `difficulty = 0.5` for any non-zero exit code. Add `0.1` for every 100 characters in `stderr`. This mathematically forces the Kernel to recognize catastrophic failures and control loss.

### 4. Urgency: Resource Depletion
*   **The Mechanic:** Token and Clock math.
*   **How it works:** `urgency = current_tokens / max_tokens`. As the agent gets closer to the context limit, urgency scales smoothly towards `1.0`.

---

## Example Implementation

The following is a theoretical implementation of a `MechanicalExtractor`. It translates raw, irrefutable OS telemetry (bytes, exit codes, hashes) into the floating-point values required by the Kernel.

```python
import hashlib

class MechanicalExtractor:
    def __init__(self, max_tokens: int):
        self.history = set()
        self.max_tokens = max_tokens

    def extract(self, tool_name: str, arguments: str, exit_code: int, stderr_len: int, bytes_changed: int, tokens_used: int) -> dict:
        signals = {
            "reward": 0.0,
            "novelty": 1.0, 
            "difficulty": 0.0,
            "urgency": min(1.0, tokens_used / self.max_tokens)
        }

        # Pure Mechanical Novelty
        action_hash = hashlib.sha256(f"{tool_name}:{arguments}".encode()).hexdigest()
        if action_hash in self.history:
            signals["novelty"] = 0.0
        else:
            self.history.add(action_hash)
        
        # Pure Mechanical Difficulty (OS-level errors)
        if exit_code != 0:
            signals["difficulty"] = min(1.0, 0.5 + (stderr_len * 0.001))
        
        # Pure Mechanical Reward (Successful State Mutation)
        if exit_code == 0 and bytes_changed > 0:
            signals["reward"] = 0.6  # It tangibly did something successful

        return signals
```

## Conclusion
By building edge adapters that translate physical system results into governance signals, you create a deeply secure governance layer that is purely mechanical. It completely sidesteps AI hallucinations because an AI cannot "hallucinate" a `0` exit code or a `400 byte` differential in disk storage.

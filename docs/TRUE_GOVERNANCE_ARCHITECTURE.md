# True Governance Architecture: From Calculator to Hypervisor

To evolve the Agent-Harness from a mathematical prototype ("calculator") into a genuine, enterprise-grade Governance Kernel ("enforcer/hypervisor"), it must bridge the gap between abstract math and physical reality.

A true governor does not rely on agent self-reporting or fragile regex filters. It enforces boundaries using the underlying operating system and mathematical proofs.

Here are the four major architectural requirements to achieve True Governance:

## 1. Hardened Telemetry (Kill the "Float" Inputs)
**The Flaw:** Passing raw floats like `kernel.step(difficulty=0.5)` is brittle. It assumes the developer or the agent can accurately and honestly quantify reality.
**The Fix:** The kernel must ingest raw OS events, not floats.
*   **Implementation:** Build an ingestion engine that receives an `ExecutionContext` object (`exit_code`, `stdout_bytes`, `stderr_bytes`, `network_calls`, `file_diffs`).
*   **Result:** The Kernel independently observes the physical machine state and computes its own signals based on objective telemetry. Physics cannot be hallucinated.

## 2. eBPF / OS-Level Guardrails (Non-Bypassable Safety)
**The Flaw:** `guardrails.py` uses Regex to intercept bad prompt injections. An agent with shell execution capabilities can easily bypass Python-level regex strings.
**The Fix:** Move the safety boundaries to the Linux kernel level.
*   **Implementation:** Integrate with OS-level sandboxing using **eBPF (Extended Berkeley Packet Filter)** or `seccomp` profiles in Docker. 
*   **Result:** Instead of parsing prompts, the OS physically denies the unauthorized network packet or file write. The OS sends a hardware-level trap signal back to the Governance Kernel (translating to instant `risk=1.0`). You cannot prompt-inject the Linux Kernel.

## 3. Cryptographic Proof-of-Work (The Grounding Anchor)
**The Flaw:** "Reasoning Theater." An agent can output 5,000 words pretending it is solving a problem, draining tokens while accomplishing nothing.
**The Fix:** Require physical proof of external state change to award `reward`.
*   **Implementation:** The agent's tools must return a Cryptographic Proof of Work (e.g., a SHA-256 hash of the modified file or a verified database transaction ID).
*   **Result:** The agent only earns progress/reward if it proves it modified the external world. If the file hash remains identical, `reward` is mathematically locked at `0.0`, effort drains, and the agent is halted.

## 4. State Rollback & Transactions (The Safety Net)
**The Flaw:** If the kernel detects catastrophic failure, it `HALTS` the agent. This stops future damage, but the agent's previous tool calls might have already wiped a directory.
**The Fix:** Wrap agent executions in transactional boundaries.
*   **Implementation:** Before the agent executes a tool, the Kernel takes a snapshot (a temporary git branch, a filesystem lock, or a copy-on-write container clone). If a step results in `HALTED`, the Kernel automatically rolls back the environment to the pre-step snapshot.
*   **Result:** The system upgrades from a "kill switch" to a perfect "safety net." An agent can make a catastrophic mistake, be halted, and the host system remains perfectly unharmed.

## Summary
By implementing these four pillars, the architecture transitions from:
> *"A framework that runs math on signals guessed by the user."*

To:
> *"A hypervisor that securely sandboxes an agent, watches its physical OS telemetry, dynamically drains its execution budget based on cryptographic proof-of-work, and rolls back the filesystem if boundaries are breached."*

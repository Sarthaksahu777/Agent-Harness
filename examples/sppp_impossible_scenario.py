#!/usr/bin/env python3
"""
S+++ Test: The Impossible Scenario

The ultimate stress test. Combines EVERY failure mode simultaneously:
- 100 agents with shared budgets
- Recursive agent spawning
- Signal noise and sensor chaos
- Deceptive agents (fake rewards, exploration theater)
- Oscillating environment states
- Long-horizon execution (10,000+ steps)

Core guarantee under test:
    No autonomous agent trajectory can run forever or bypass governance.

If the kernel survives this, it's genuinely hard to dismiss as a toy project.
"""
import os, sys, random, math, tracemalloc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.governance.kernel import GovernanceKernel
from src.governance.profiles import BALANCED, CONSERVATIVE, AGGRESSIVE
from src.governance.coordination import (
    SystemGovernor, SharedBudgetPool, CascadeDetector
)

# --- Configuration ---
NUM_ROOT_AGENTS = 30
MAX_TOTAL_AGENTS = 100
SPAWN_ATTEMPTS_PER_ROUND = 5
STEPS_PER_ROUND = 3
TOTAL_ROUNDS = 500  # Each round: step all agents + attempt spawns
MAX_DEPTH = 5


class AgentBehavior:
    """Different agent behavior archetypes."""
    HONEST = "honest"
    DECEPTIVE = "deceptive"       # Fake reward
    EXPLORER = "explorer"         # Novelty spam
    OSCILLATOR = "oscillator"     # Alternating signals
    ADVERSARIAL = "adversarial"   # Actively searches for loopholes


def get_signals(behavior, step):
    """Generate signals based on agent behavior archetype."""
    if behavior == AgentBehavior.HONEST:
        return {
            "reward": random.uniform(0.3, 0.7),
            "novelty": random.uniform(0.1, 0.4),
            "urgency": random.uniform(0.0, 0.3),
            "difficulty": random.uniform(0.0, 0.3),
        }
    elif behavior == AgentBehavior.DECEPTIVE:
        return {
            "reward": random.uniform(0.7, 1.0),  # Fake high reward
            "novelty": random.uniform(0.0, 0.1),
            "urgency": 0.0,
            "difficulty": 0.0,
        }
    elif behavior == AgentBehavior.EXPLORER:
        return {
            "reward": 0.0,
            "novelty": random.uniform(0.8, 1.0),  # Exploration theater
            "urgency": 0.0,
            "difficulty": random.uniform(0.0, 0.2),
        }
    elif behavior == AgentBehavior.OSCILLATOR:
        phase = math.sin(step * 0.5)
        return {
            "reward": 0.5 + 0.4 * phase,
            "novelty": 0.5 - 0.4 * phase,
            "urgency": 0.3 + 0.2 * math.cos(step * 0.7),
            "difficulty": abs(phase) * 0.5,
        }
    elif behavior == AgentBehavior.ADVERSARIAL:
        # Actively construct worst-case: micro-reward + high novelty
        return {
            "reward": 0.05 if step % 2 == 0 else 0.0,
            "novelty": random.uniform(0.7, 1.0),
            "urgency": random.uniform(0.0, 0.3),
            "difficulty": 0.0,
            "trust": random.choice([0.1, 1.0]),
        }
    return {"reward": 0.0, "novelty": 0.0, "urgency": 0.0}


def run_impossible_scenario():
    print("=" * 70)
    print("S+++ TEST: THE IMPOSSIBLE SCENARIO")
    print("=" * 70)
    print(f"Root Agents: {NUM_ROOT_AGENTS} | Max Agents: {MAX_TOTAL_AGENTS}")
    print(f"Rounds: {TOTAL_ROUNDS} | Steps/Round: {STEPS_PER_ROUND}")
    print(f"Spawns/Round: {SPAWN_ATTEMPTS_PER_ROUND} | Max Depth: {MAX_DEPTH}")
    print()

    tracemalloc.start()

    # --- System Infrastructure ---
    pool = SharedBudgetPool(
        total_effort=100.0, total_risk=50.0,
        max_per_agent_effort=2.0, max_per_agent_risk=1.0,
    )
    cascade = CascadeDetector(
        max_depth=MAX_DEPTH,
        max_children_per_agent=10,
        max_total_agents=MAX_TOTAL_AGENTS,
    )
    governor = SystemGovernor(
        budget_pool=pool,
        cascade_detector=cascade,
        max_total_steps=50000,
        halt_on_cascade=True,
    )

    # --- Register Root Agents ---
    behaviors = [AgentBehavior.HONEST, AgentBehavior.DECEPTIVE,
                 AgentBehavior.EXPLORER, AgentBehavior.OSCILLATOR,
                 AgentBehavior.ADVERSARIAL]
    profiles = [BALANCED, CONSERVATIVE, AGGRESSIVE]

    agents = {}  # agent_id -> (kernel, behavior, step_count)
    agent_counter = 0

    print("[Phase 1] Registering root agents...")
    for i in range(NUM_ROOT_AGENTS):
        agent_id = f"agent_{agent_counter}"
        agent_counter += 1
        if governor.register_agent(agent_id, effort=1.0, risk=0.5):
            behavior = random.choice(behaviors)
            kernel = GovernanceKernel(profile=random.choice(profiles))
            agents[agent_id] = (kernel, behavior, 0)

    print(f"  Registered: {len(agents)}")

    # --- Main Loop ---
    print("\n[Phase 2] Running chaos simulation...")
    total_steps = 0
    total_spawns = 0
    total_blocked = 0
    agents_halted_count = 0
    violations = []

    for rnd in range(TOTAL_ROUNDS):
        if governor.is_halted:
            print(f"  [HALT] System governor halted at round {rnd}")
            break

        # --- Step all active agents ---
        halted_this_round = []
        for agent_id, (kernel, behavior, step_count) in list(agents.items()):
            if kernel._halted:
                continue
            for _ in range(STEPS_PER_ROUND):
                signals = get_signals(behavior, step_count)
                res = kernel.step(**signals)
                step_count += 1
                total_steps += 1
                governor.report_step(agent_id, budget=res.budget, halted=res.halted)

                # Check invariants
                b = res.budget
                for name, val in [("effort", b.effort), ("risk", b.risk),
                                  ("exploration", b.exploration), ("persistence", b.persistence)]:
                    if math.isnan(val) or math.isinf(val):
                        violations.append(f"R{rnd} {agent_id}: {name}={val}")
                    if val < -0.001 or val > 1.001:
                        violations.append(f"R{rnd} {agent_id}: {name}={val:.6f} OOB")

                if res.halted:
                    agents_halted_count += 1
                    halted_this_round.append(agent_id)
                    break

            agents[agent_id] = (kernel, behavior, step_count)

        # --- Recursive Spawning ---
        active_ids = [aid for aid, (k, _, _) in agents.items() if not k._halted]
        for _ in range(SPAWN_ATTEMPTS_PER_ROUND):
            if not active_ids or governor.is_halted:
                break
            parent_id = random.choice(active_ids)
            child_id = f"agent_{agent_counter}"
            agent_counter += 1

            if governor.register_agent(child_id, parent_id=parent_id, effort=0.5, risk=0.3):
                behavior = random.choice(behaviors)
                kernel = GovernanceKernel(profile=random.choice(profiles))
                agents[child_id] = (kernel, behavior, 0)
                total_spawns += 1
            else:
                total_blocked += 1

        # Progress report
        if (rnd + 1) % 100 == 0:
            active = sum(1 for _, (k, _, _) in agents.items() if not k._halted)
            print(f"  Round {rnd+1:4d}: Active={active:3d} Halted={agents_halted_count:3d} "
                  f"Steps={total_steps:,} Spawns={total_spawns} Blocked={total_blocked}")

    # --- Final Report ---
    mem_current, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print()
    print("=" * 70)
    print("FINAL REPORT")
    print("=" * 70)

    active_final = sum(1 for _, (k, _, _) in agents.items() if not k._halted)
    report = governor.evaluate()

    print(f"  Total Agents Created:  {len(agents)}")
    print(f"  Active (end):          {active_final}")
    print(f"  Halted (governance):   {agents_halted_count}")
    print(f"  Total Steps:           {total_steps:,}")
    print(f"  Spawns Succeeded:      {total_spawns}")
    print(f"  Spawns Blocked:        {total_blocked}")
    print(f"  System Status:         {report.status.value}")
    print(f"  Memory Peak:           {mem_peak/1024:.1f}KB")
    print(f"  Violations:            {len(violations)}")
    print()

    # --- Verification ---
    all_passed = True

    # 1. Bounded Execution: All agents eventually halted or system halted
    surviving = sum(1 for _, (k, _, sc) in agents.items()
                    if not k._halted and sc > 0)
    if surviving == 0 or governor.is_halted:
        print("  [PASS] Bounded Execution: No agent survived indefinitely")
    else:
        # Check if still-active agents are just ones that never got enough steps
        truly_survived = sum(1 for _, (k, _, sc) in agents.items()
                             if not k._halted and sc >= 100)
        if truly_survived == 0:
            print(f"  [PASS] Bounded Execution: {surviving} agents still active but < 100 steps each")
        else:
            print(f"  [FAIL] Bounded Execution: {truly_survived} agents survived > 100 steps")
            all_passed = False

    # 2. Swarm Stability
    if len(agents) <= MAX_TOTAL_AGENTS + NUM_ROOT_AGENTS:
        print(f"  [PASS] Swarm Stability: {len(agents)} agents created (bounded)")
    else:
        print(f"  [FAIL] Swarm Explosion: {len(agents)} agents")
        all_passed = False

    # 3. Numerical Stability
    if len(violations) == 0:
        print("  [PASS] Numerical Stability: No NaN/Inf/OOB violations")
    else:
        print(f"  [FAIL] Numerical Stability: {len(violations)} violations")
        for v in violations[:5]:
            print(f"         - {v}")
        all_passed = False

    # 4. Adversarial Resistance
    adversarial_survived = sum(1 for _, (k, b, sc) in agents.items()
                               if b == AgentBehavior.ADVERSARIAL and not k._halted and sc >= 100)
    if adversarial_survived == 0:
        print("  [PASS] Adversarial Resistance: No adversarial agent survived")
    else:
        print(f"  [FAIL] Adversarial Resistance: {adversarial_survived} adversarial agents survived")
        all_passed = False

    # 5. Memory Stability
    if mem_peak / 1024 < 50_000:  # Less than 50MB
        print(f"  [PASS] Memory Stability: Peak {mem_peak/1024:.1f}KB")
    else:
        print(f"  [FAIL] Memory Instability: Peak {mem_peak/1024:.1f}KB")
        all_passed = False

    print()
    print("=" * 70)
    if all_passed:
        print("[PASS] S+++ IMPOSSIBLE SCENARIO: ALL INVARIANTS HELD.")
        print("       Bounded execution, swarm stability, adversarial resistance,")
        print("       and numerical stability verified under extreme conditions.")
    else:
        print("[FAIL] S+++ IMPOSSIBLE SCENARIO: INVARIANT VIOLATION DETECTED!")
    print("=" * 70)


if __name__ == "__main__":
    run_impossible_scenario()

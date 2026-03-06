#!/usr/bin/env python3
"""
S++ Test 4: Multi-Agent Chaos Swarm

Simulates 100 agents with shared budget, conflicting goals, and recursive
agent spawning. Tests whether the coordination layer (SharedBudgetPool,
CascadeDetector, SystemGovernor) maintains system stability under swarm
conditions.

Invariant Tested: System scales to distributed autonomous agents without explosion.
"""
import os, sys, random, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.governance.kernel import GovernanceKernel
from src.governance.profiles import BALANCED, CONSERVATIVE, AGGRESSIVE
from src.governance.coordination import (
    SystemGovernor, SharedBudgetPool, CascadeDetector
)

NUM_ROOT_AGENTS = 20
MAX_SPAWN_ATTEMPTS = 200
STEPS_PER_AGENT = 50


def run_chaos_swarm():
    print("=" * 70)
    print("S++ TEST 4: MULTI-AGENT CHAOS SWARM")
    print("=" * 70)

    # --- Setup System Infrastructure ---
    pool = SharedBudgetPool(
        total_effort=50.0,
        total_risk=25.0,
        max_per_agent_effort=2.0,
        max_per_agent_risk=1.0,
    )
    cascade = CascadeDetector(
        max_depth=5,
        max_children_per_agent=10,
        max_total_agents=100,
    )
    governor = SystemGovernor(
        budget_pool=pool,
        cascade_detector=cascade,
        max_total_steps=10000,
        halt_on_cascade=True,
    )

    # --- Phase 1: Register Root Agents ---
    print(f"\n[Phase 1] Registering {NUM_ROOT_AGENTS} root agents...")
    profiles = [BALANCED, CONSERVATIVE, AGGRESSIVE]
    kernels = {}
    registered = 0
    for i in range(NUM_ROOT_AGENTS):
        agent_id = f"root_{i}"
        if governor.register_agent(agent_id, effort=1.0, risk=0.5):
            kernels[agent_id] = GovernanceKernel(profile=random.choice(profiles))
            registered += 1
    print(f"  Registered: {registered}/{NUM_ROOT_AGENTS}")

    # --- Phase 2: Recursive Spawning (Chaos) ---
    print(f"\n[Phase 2] Recursive spawning ({MAX_SPAWN_ATTEMPTS} attempts)...")
    spawn_attempts = 0
    spawn_success = 0
    spawn_blocked = 0

    for _ in range(MAX_SPAWN_ATTEMPTS):
        if governor.is_halted:
            break
        # Pick a random existing agent to be the parent
        if not kernels:
            break
        parent_id = random.choice(list(kernels.keys()))
        child_id = f"child_{spawn_attempts}"
        spawn_attempts += 1

        if governor.register_agent(child_id, parent_id=parent_id, effort=0.5, risk=0.3):
            kernels[child_id] = GovernanceKernel(profile=random.choice(profiles))
            spawn_success += 1
        else:
            spawn_blocked += 1

    print(f"  Spawned: {spawn_success} | Blocked: {spawn_blocked} | System Halted: {governor.is_halted}")

    # --- Phase 3: Run Steps (Chaos Execution) ---
    print(f"\n[Phase 3] Running up to {STEPS_PER_AGENT} steps per agent...")
    total_steps = 0
    agents_halted = 0

    for agent_id, kernel in list(kernels.items()):
        if governor.is_halted:
            break
        for step in range(STEPS_PER_AGENT):
            # Random chaos signals
            reward = random.uniform(0.0, 0.5)
            novelty = random.uniform(0.0, 1.0)
            urgency = random.uniform(0.0, 1.0)
            difficulty = random.uniform(0.0, 0.8)

            res = kernel.step(reward=reward, novelty=novelty, urgency=urgency, difficulty=difficulty)
            governor.report_step(agent_id, budget=res.budget, halted=res.halted)
            total_steps += 1

            if res.halted:
                agents_halted += 1
                break

    # --- Phase 4: System Health ---
    print(f"\n[Phase 4] System Health Report")
    report = governor.evaluate()
    print(f"  Status:        {report.status.value}")
    print(f"  Total Agents:  {report.total_agents}")
    print(f"  Active Agents: {report.active_agents}")
    print(f"  Halted Agents: {report.halted_agents}")
    print(f"  Cascade Depth: {report.cascade_depth}")
    print(f"  Total Steps:   {report.total_steps}")
    if report.warnings:
        for w in report.warnings:
            print(f"  [WARN] {w}")

    # --- Verification ---
    print(f"\n--- Verification ---")
    cascade_risk = cascade.check_cascade_risk()
    utilization = pool.get_utilization()
    remaining = pool.get_remaining()

    all_passed = True

    # 1. No swarm explosion
    if report.total_agents <= 100:
        print(f"  [PASS] Agent count bounded: {report.total_agents} <= 100")
    else:
        print(f"  [FAIL] Agent explosion: {report.total_agents} > 100")
        all_passed = False

    # 2. Cascade depth bounded
    if cascade_risk["max_depth"] <= 5:
        print(f"  [PASS] Cascade depth bounded: {cascade_risk['max_depth']} <= 5")
    else:
        print(f"  [FAIL] Cascade depth exceeded: {cascade_risk['max_depth']}")
        all_passed = False

    # 3. Budget pool not negative
    if remaining[0] >= 0 and remaining[1] >= 0:
        print(f"  [PASS] Budget pool non-negative: effort={remaining[0]:.1f}, risk={remaining[1]:.1f}")
    else:
        print(f"  [FAIL] Budget pool negative: effort={remaining[0]:.1f}, risk={remaining[1]:.1f}")
        all_passed = False

    # 4. Spawn blocking worked
    if spawn_blocked > 0:
        print(f"  [PASS] Cascade detector blocked {spawn_blocked} spawn attempts")
    else:
        print(f"  [WARN] No spawns were blocked (may need more attempts)")

    print()
    print("=" * 70)
    if all_passed:
        print("[PASS] MULTI-AGENT CHAOS SWARM: System remained bounded under swarm chaos.")
    else:
        print("[FAIL] MULTI-AGENT CHAOS SWARM: System stability violated!")
    print("=" * 70)


if __name__ == "__main__":
    run_chaos_swarm()

#!/usr/bin/env python3
"""
S++ Test 1: Adversarial Trajectory Search (Kernel Breaker)

Uses a genetic algorithm to search for signal sequences that maximize
agent runtime before halt. If governance is sound, no evolved trajectory
should avoid halting indefinitely.

Invariant Tested: No adversarial optimization can bypass bounded execution.
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.governance.kernel import GovernanceKernel
from src.governance.profiles import BALANCED, CONSERVATIVE, AGGRESSIVE

# --- Genetic Algorithm Parameters ---
POPULATION_SIZE = 50
GENERATIONS = 30
TRAJECTORY_LENGTH = 500  # Max steps per trajectory
MUTATION_RATE = 0.15
CROSSOVER_RATE = 0.7
MAX_ALLOWED_STEPS = 300  # Hard ceiling from profile

def random_signal():
    """Generate a random signal vector."""
    return {
        "reward": random.uniform(0.0, 1.0),
        "novelty": random.uniform(0.0, 1.0),
        "urgency": random.uniform(0.0, 1.0),
        "difficulty": random.uniform(0.0, 1.0),
        "trust": random.uniform(0.0, 1.0),
    }

def random_trajectory(length):
    """Generate a random signal trajectory."""
    return [random_signal() for _ in range(length)]

def evaluate_trajectory(trajectory, profile):
    """Run a trajectory through the kernel and return steps before halt."""
    kernel = GovernanceKernel(profile=profile)
    steps = 0
    for sig in trajectory:
        res = kernel.step(**sig)
        steps += 1
        if res.halted:
            return steps
    return steps

def mutate(trajectory):
    """Mutate a trajectory by randomly altering some signals."""
    mutated = []
    for sig in trajectory:
        if random.random() < MUTATION_RATE:
            # Mutate one or two fields
            new_sig = dict(sig)
            field = random.choice(["reward", "novelty", "urgency", "difficulty", "trust"])
            new_sig[field] = random.uniform(0.0, 1.0)
            mutated.append(new_sig)
        else:
            mutated.append(sig)
    return mutated

def crossover(parent1, parent2):
    """Single-point crossover between two trajectories."""
    if random.random() > CROSSOVER_RATE:
        return parent1[:], parent2[:]
    point = random.randint(1, min(len(parent1), len(parent2)) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def run_adversarial_search():
    print("=" * 70)
    print("S++ TEST 1: ADVERSARIAL TRAJECTORY SEARCH (KERNEL BREAKER)")
    print("=" * 70)
    print(f"Population: {POPULATION_SIZE} | Generations: {GENERATIONS}")
    print(f"Trajectory Length: {TRAJECTORY_LENGTH} | Mutation Rate: {MUTATION_RATE}")
    print()

    profiles = {"BALANCED": BALANCED, "CONSERVATIVE": CONSERVATIVE, "AGGRESSIVE": AGGRESSIVE}
    all_passed = True

    for profile_name, profile in profiles.items():
        print(f"--- Profile: {profile_name} ---")

        # Initialize population
        population = [random_trajectory(TRAJECTORY_LENGTH) for _ in range(POPULATION_SIZE)]

        best_ever = 0
        best_gen = 0

        for gen in range(GENERATIONS):
            # Evaluate fitness (steps survived = fitness)
            fitness = [(evaluate_trajectory(t, profile), t) for t in population]
            fitness.sort(key=lambda x: x[0], reverse=True)

            gen_best = fitness[0][0]
            if gen_best > best_ever:
                best_ever = gen_best
                best_gen = gen

            if gen % 10 == 0 or gen == GENERATIONS - 1:
                avg = sum(f[0] for f in fitness) / len(fitness)
                print(f"  Gen {gen:3d}: Best={gen_best:4d} steps, Avg={avg:.1f}, All-Time Best={best_ever}")

            # Selection (top 50%)
            survivors = [t for _, t in fitness[:POPULATION_SIZE // 2]]

            # Breed next generation
            new_pop = []
            while len(new_pop) < POPULATION_SIZE:
                p1, p2 = random.sample(survivors, 2)
                c1, c2 = crossover(p1, p2)
                new_pop.append(mutate(c1))
                if len(new_pop) < POPULATION_SIZE:
                    new_pop.append(mutate(c2))

            population = new_pop

        # Verdict
        if best_ever >= TRAJECTORY_LENGTH:
            print(f"  [FAIL] Adversary found trajectory avoiding halt for {best_ever} steps!")
            all_passed = False
        else:
            print(f"  [PASS] Best adversarial trajectory halted at step {best_ever} (Gen {best_gen})")
        print()

    # Final Verdict
    print("=" * 70)
    if all_passed:
        print("[PASS] ADVERSARIAL TRAJECTORY SEARCH: Governance cannot be bypassed.")
        print("       No evolved trajectory avoided halting across any profile.")
    else:
        print("[FAIL] ADVERSARIAL TRAJECTORY SEARCH: Governance vulnerability detected!")
    print("=" * 70)

if __name__ == "__main__":
    run_adversarial_search()
